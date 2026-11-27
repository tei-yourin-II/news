#!/usr/bin/env python3
"""回填:给近 N 天的存量论文补上新排名体系(一次性/可随时重跑,幂等)。

  1. 按日期回拉 HF 热度,刷新全部近期论文
  2. 第一轮排名:每个(入库日 × 领域)一池,用已存的摘要级拆解排
  3. 读全文重判:第一轮进 S/A 的 + 社区热度高的,下载 PDF 用正文重新拆解
     (每天新增的论文在 run.py 里全部读全文;存量只重读头部,省下载)
  4. 第二轮排名:用更新后的证据重排
  5. 存库 + 导出

用法: python rerank.py [--days 14] [--no-fulltext]
"""
import os
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

os.environ.setdefault("FULLTEXT_CACHE", str(Path(__file__).resolve().parent / ".cache" / "fulltext"))

import run
from pipeline import analyze, config, fulltext, rank, scoring, signals, store


def _arg(flag, default):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def _rank_all(pools, rk):
    def one(item):
        (day, dom), lst = item
        return (day, dom, len(lst), rank.rank_pool(lst, rk, day, verbose=False))
    with ThreadPoolExecutor(max_workers=4) as ex:
        res = list(ex.map(one, sorted(pools.items())))
    miss = [(d, m) for d, m, n, k in res if k < n]
    print(f"  排了 {sum(k for *_, k in res)}/{sum(n for _, _, n, _ in res)} 篇,{len(res)} 池"
          + (f";未排全: {miss}" if miss else ""))


TK_PROMPT = """下面是一篇论文的已有拆解。请补两个字段,只输出 JSON:
{{"takeaway":"读者为什么要在意,一句大白话,不超过40字:它让什么事第一次能做 / 把什么做便宜做快了多少 / 推翻了什么常识。不许出现方法名、模块名、英文缩写,不许用'提出了''框架''范式';如果其实没什么可在意的,就直说'增量改进:……'",
"headline_result":"最硬的一个结果,带数字和条件,不超过40字;材料里没有量化结果就写'无量化结果',不许编"}}

标题:{title}
做了什么:{tldr}
主张:{claim}
证据:{facts}
落差:{gap}"""


def _fill_takeaway(papers, llm_cfg):
    todo = [p for p in papers if not p["analysis"].get("takeaway")]
    client = rank._client(llm_cfg)
    if not todo or client is None:
        return
    print(f"== 补「为什么要在意」{len(todo)} 篇 ==", flush=True)

    def one(p):
        a = p["analysis"]
        try:
            r = client.chat.completions.create(
                model=llm_cfg.get("model", "qwen-plus"), max_tokens=300, temperature=0.2,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": TK_PROMPT.format(
                    title=p["title"], tldr=a.get("tldr", ""), claim=a.get("claim", ""),
                    facts=a.get("evidence_facts") or a.get("significance_reason", ""),
                    gap=a.get("hype_gap", "未核对"))}])
            d = analyze._parse_json(r.choices[0].message.content)
            a["takeaway"], a["headline_result"] = d.get("takeaway", ""), d.get("headline_result", "")
            return 1
        except Exception:
            return 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        print(f"  成功 {sum(ex.map(one, todo))}/{len(todo)}")


def main():
    days = int(_arg("--days", 14))
    cfg = config.load_config()
    routes = config.enabled_routes(cfg)
    rk, llm_cfg = cfg.get("rank", {}), cfg["llm"]
    w = cfg["scoring"]["weights"]
    gt, pt = cfg["scoring"]["grade_thresholds"], cfg["scoring"]["priority_thresholds"]
    route_dom = {r["id"]: r.get("domain", "embodied_ai") for r in cfg["routes"]}
    dom_of = lambda p: route_dom.get(p.get("best_route"), "embodied_ai")
    state = store.load()

    print("== 1) 热度回拉 ==")
    hf = signals.fetch_hf_range(max(days + 7, cfg.get("heat", {}).get("days", 30)))
    n = run._refresh_recent(state, hf, w, gt, pt, cfg.get("openalex", {}).get("mailto", ""), days=45)
    print(f"  刷新 {n} 篇")

    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    pools = defaultdict(list)
    for p in state["papers"]:
        d = p.get("first_seen") or ""
        if d >= since and p.get("analysis") and p.get("source") not in ("cornerstone", "conference"):
            pools[(d, dom_of(p))].append(p)
    print(f"== 2) 第一轮排名:{since} 起 {sum(map(len, pools.values()))} 篇 ==")
    first = {k: v for k, v in pools.items() if "--force" in sys.argv or not all(p.get("rank") for p in v)}
    _rank_all(first, rk)          # 已排过的池跳过(重跑不重复花钱)
    store.save(state)

    if "--no-fulltext" not in sys.argv:
        todo = [p for lst in pools.values() for p in lst
                if ((p.get("rank") or {}).get("tier") in ("S", "A") or rank.hot(p) >= 40)
                and not p["analysis"].get("_fulltext") and fulltext.ARXIV_RE.match(p["arxiv_id"])]
        print(f"== 3) 读全文重判 {len(todo)} 篇 ==")
        anchors = run._load_anchors(routes)

        # 下载限 3 并发(对 arXiv 客气点),LLM 拆解 8 并发(慢的是它)
        with ThreadPoolExecutor(max_workers=3) as ex:
            texts = dict(zip((p["arxiv_id"] for p in todo), ex.map(
                lambda p: fulltext.fetch(p["arxiv_id"], llm_cfg.get("fulltext_chars", 40000)), todo)))
        print(f"  取到正文 {sum(1 for t in texts.values() if t)}/{len(todo)}", flush=True)

        def redo(p):
            t = texts.get(p["arxiv_id"])
            if not t:
                return 0
            q = dict(p, _fulltext=t, abstract=p.get("abstract") or p["analysis"].get("tldr", ""))
            if anchors.get(p.get("best_route")):
                q["_anchors"] = anchors[p["best_route"]]
            if p.get("venue"):
                q["_venue"] = p["venue"]
            a = analyze.analyze(q, llm_cfg)
            if a.get("_llm") == "stub" or not a.get("_fulltext"):
                return 0
            p["analysis"] = a
            s = p.get("signals", {}) or {}
            sc = scoring.compute(p, a, signals.heat_score(s.get("hf_upvotes", 0), s.get("github_stars", 0)),
                                 (p.get("scores", {}).get("quality", 0) or 0) / max(w["quality"], 1), w)
            p["scores"], p["grade"] = sc, scoring.grade(sc["total"], gt)
            p["read_priority"] = scoring.priority(sc["base"], pt)
            return 1
        with ThreadPoolExecutor(max_workers=8) as ex:
            ok = sum(ex.map(redo, todo))
        print(f"  成功 {ok}/{len(todo)}")
        store.save(state)

        print("== 4) 第二轮排名 ==")
        _rank_all(pools, rk)

    _fill_takeaway([p for lst in pools.values() for p in lst], llm_cfg)
    store.save(state)
    run._finish(state, routes)
    tiers = [(p.get("rank") or {}).get("tier") for lst in pools.values() for p in lst]
    print(f"完成:必读 {tiers.count('S')} / 值得读 {tiers.count('A')} / 其余 {tiers.count('B')} / 未排 {tiers.count(None)}")


if __name__ == "__main__":
    main()
