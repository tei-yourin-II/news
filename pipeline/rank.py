"""同批强制排名:把同一领域、同一天入库的论文放在一起,让 LLM 排先后并限额分档。

为什么不用逐篇打的 significance 排序:逐篇打绝对分时模型没有参照,结果一半论文挤在 68~78,
排序等于随机。放在一起比、且头部名额有限,才分得出高下。

产出写到 paper["rank"] = {"tier": "S|A|B", "merit": 0~100, "why": 一句话, "date", "pool"}。
  S 必读(约 6%,至少 1 篇)/ A 值得读(约 20%)/ B 其余。
merit 只看内容,不看热度;热度是另一条独立的轴(signals.hot_score),两者在 combo() 里合成。
"""
import json
import os

from . import signals
from .analyze import _OPENAI_COMPAT, _parse_json, _resolve_key

GROUP = 45          # 一次最多比多少篇(再多 LLM 排不准,拆组)

PROMPT = """你是具身智能/脑机接口/AI×科学方向的资深编辑,要从下面 {n} 篇**同一天**的新论文里排出先后。
读者是该领域的研究者,时间只够读头部几篇。

判断"重要"的标准(按实质,不按措辞):
- 做成了以前做不成的事,且有扎实证据(真机、多任务、有对比和消融);
- 开了一个别人会跟进的方向,或放出了别人会直接拿去用的模型/数据/系统;
- 头部团队拿出的有真实证据的工作(只挂名头、没证据的不算)。
要压低的:只有仿真小实验却写得很大、换皮组合、没有新结论的 benchmark、纯设想的立场文章、
"首次/突破/通用"等词很多但 evidence 里查不到对应事实的。看每篇的「落差」一栏。

硬性名额(必须遵守,宁缺毋滥):
- S(必读)最多 {ns} 篇;没有够格的可以少于这个数,但不能多。
- A(值得读)最多 {na} 篇。
- 其余都是 B。

论文列表:
{items}

只输出 JSON,不要 markdown:
{{"order":[按重要性从高到低排的全部编号],"S":[编号],"A":[编号],
"why":{{"编号":"一句中文,说清它凭什么排在这档(只给 S 和 A 写)"}}}}"""


def _item(i, p):
    a = p.get("analysis", {}) or {}
    facts = a.get("evidence_facts") or (
        f"{a.get('sim2real_status', '')} / 开源:{a.get('reproducibility', '')} / {a.get('significance_reason', '')}")
    gap = a.get("hype_gap") or "(未核对正文)"
    venue = f" | 录用:{p['venue']}" if p.get("venue") else ""
    return (f"[{i}] {p['title']}\n    机构:{a.get('org', 'unknown')}{venue}\n"
            f"    做了什么:{a.get('tldr', '')}\n    证据:{facts}\n    落差:{gap}")


def _client(cfg):
    provider = cfg.get("provider", "qwen")
    if provider not in _OPENAI_COMPAT:
        return None
    key = _resolve_key(_OPENAI_COMPAT[provider]["key_envs"])
    if not key:
        return None
    try:
        from openai import OpenAI
    except ImportError:
        return None
    return OpenAI(api_key=key, base_url=cfg.get("base_url") or _OPENAI_COMPAT[provider]["base_url"])


def _sig(p):
    return (p.get("analysis", {}) or {}).get("significance", 0) or 0


def _rank_group(client, model, group):
    n = len(group)
    ns, na = max(1, round(n * 0.06)), max(1, round(n * 0.2))
    prompt = PROMPT.format(n=n, ns=ns, na=na,
                           items="\n".join(_item(i, p) for i, p in enumerate(group)))
    resp = client.chat.completions.create(
        model=model, max_tokens=3000, temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}])
    d = _parse_json(resp.choices[0].message.content)
    ok = lambda xs: [int(x) for x in (xs or []) if str(x).lstrip("-").isdigit() and 0 <= int(x) < n]
    S = list(dict.fromkeys(ok(d.get("S"))))[:ns]
    A = [x for x in dict.fromkeys(ok(d.get("A"))) if x not in S][:na]
    order = list(dict.fromkeys(ok(d.get("order"))))
    rest = [i for i in sorted(range(n), key=lambda i: -_sig(group[i])) if i not in order]
    order += rest                                   # LLM 漏排的按旧分量分垫在后面
    pos = {x: k for k, x in enumerate(order)}
    S.sort(key=pos.get); A.sort(key=pos.get)
    B = [x for x in order if x not in S and x not in A]
    why = {str(k): v for k, v in (d.get("why") or {}).items()}
    out = {}
    for tier, xs, hi, span in (("S", S, 100, 10), ("A", A, 89, 19), ("B", B, 65, 45)):
        for k, x in enumerate(xs):
            out[x] = {"tier": tier, "merit": round(hi - span * k / max(len(xs), 1), 1),
                      "why": why.get(str(x), "")}
    return out


def rank_pool(papers, cfg, date, verbose=True):
    """对一批(同域同日)论文排名,原地写 p['rank']。失败则不写(页面退回旧分量分)。"""
    if not papers:
        return 0
    client = _client(cfg)
    if client is None:
        return 0
    model = cfg.get("model", "qwen-max")
    papers = sorted(papers, key=lambda p: p["arxiv_id"])
    k = max(1, -(-len(papers) // GROUP))            # 组数
    groups = [papers[i::k] for i in range(k)]
    done = 0
    for g in groups:
        try:
            res = _rank_group(client, model, g)
        except Exception as e:
            if verbose:
                print(f"  [rank] 一组({len(g)} 篇)排名失败,跳过: {e}")
            continue
        for i, p in enumerate(g):
            if i in res:
                p["rank"] = dict(res[i], date=date, pool=len(g))
                done += 1
    return done


def calibrate_legacy(papers, dom_of):
    """没参加过同批排名的老论文:把旧分量分按「同月 × 同领域」内的名次换算到同一把尺子
    (前 6% → S 90~100,接下来 20% → A 70~89,其余 → B 20~65),写入 p["rank"](legacy=True)。
    旧分一半挤在 68~78,直接用会和新排名不可比;打折又等于变相给老论文降权。
    按名次换算不花 LLM 钱,也不带时间权重。同分的用内容分、热度依次破平。基石/顶会论文不动。"""
    pools = {}
    for p in papers:
        if p.get("rank") and not p["rank"].get("legacy"):
            continue
        if p.get("source") in ("cornerstone", "conference") or not p.get("analysis"):
            continue
        month = (p.get("first_seen") or p.get("published") or "")[:7]
        pools.setdefault((month, dom_of(p)), []).append(p)
    n_done = 0
    for (month, _), lst in pools.items():
        lst.sort(key=lambda p: (_sig(p), (p.get("scores") or {}).get("content", 0), hot(p)), reverse=True)
        n = len(lst)
        ns, na = max(1, round(n * 0.06)), max(1, round(n * 0.2))
        for k, p in enumerate(lst):
            if k < ns:
                tier, m = "S", 100 - 10 * k / ns
            elif k < ns + na:
                tier, m = "A", 89 - 19 * (k - ns) / na
            else:
                tier, m = "B", 65 - 45 * (k - ns - na) / max(n - ns - na, 1)
            # 旧分本身很低的(作者自己都没证据)不因为"那个月人少"被抬进头部
            if _sig(p) < 60 and tier != "B":
                tier, m = "B", min(m, 65)
            p["rank"] = {"tier": tier, "merit": round(m, 1), "why": "", "date": month,
                         "pool": n, "legacy": True}
            n_done += 1
    return n_done


# ---------- 展示用的两条轴 + 合成 ----------
def hot(p):
    s = p.get("signals", {}) or {}
    return signals.hot_score(s.get("hf_upvotes", 0), s.get("github_stars", 0))


def merit(p):
    """内容分 0~100。排过名的用排名分;没排过的(老论文)用旧分量分打七折垫底——
    旧分普遍虚高,不能和排名分平起平坐。"""
    r = p.get("rank")
    if r:
        return r["merit"]
    if p.get("source") in ("cornerstone", "conference"):   # 人工挑的基石/顶会论文,分量分可信,不打折
        return _sig(p)
    return round(_sig(p) * 0.7, 1)


def combo(p):
    """综合 = 内容和热度里高的那个占七成、低的占三成。
    任何一条轴突出都能上榜,两条都突出的排最前。"""
    m, h = merit(p), hot(p)
    return round(0.7 * max(m, h) + 0.3 * min(m, h), 1)
