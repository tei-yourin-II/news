#!/usr/bin/env python3
"""小红书文案生成:把「今日精选」论文 → 结构化 JSON(封面 + 分页内容块)。

核心设计:LLM 只填**语义**,不碰颜色/字体/排版。
  - 每块只给 type(lead/p/num/li/sec/card/tags),颜色由前端 CSS 按 type 固定;
  - 行内强调用 **…** 标记(只标真实数字/关键术语),前端把 **x** 渲成 <b>(CSS 上色);
  - 这样无论 LLM 写什么,排版与配色永远一致、不会翻车。

产物:
  - 写回 docs/daily_picks.json 对应 pick 的 "xhs" 字段(沉淀,随精选归档);
  - 同时写 docs/xhs_sample.json(最近一次生成,供 xhs_preview.html 直接 fetch 预览)。

用法:
  python gen_xhs.py                # 给「最新一天分量最高的精选」生成
  python gen_xhs.py --id 2606.06033
  python gen_xhs.py --date 2026-06-07 --all   # 给该日全部精选生成
"""
import json
import sys
from pathlib import Path

from pipeline import analyze, config

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
PICKS = DOCS / "daily_picks.json"
WEEKLY = DOCS / "weekly_picks.json"
DATA = DOCS / "data.json"
STORE = DOCS / "xhs_store.json"          # 一般化产物:by_id 存所有已生成的小红书 JSON
SAMPLE = DOCS / "xhs_sample.json"        # 最近一次(供 preview 默认/兜底)


SYSTEM = """你把一篇具身智能/机器人方向的论文,改写成一篇**适合发小红书的「每日论文精选」**,只输出一个 JSON 对象。

读者是关注具身智能的工程师与认真的爱好者。要求:**客观概要这篇论文**(它解决什么、怎么做、实测结果、论文写明的局限),
**不要下主观判断**——禁止"突破/颠覆/碾压/里程碑/范式级/必读"之类评价词,也不要打分。吸引眼球只允许出现在封面标题和开头第一句(lead),正文老老实实讲事实。

⚠️ 严禁编造数字:只能引用我给你的材料里**明确出现**的数值/指标/数据集名,没有就定性描述,绝不瞎编(这是要发出去的,编造=翻车)。

【输出 JSON 结构】
{
  "cover": {
    "tag": "领域 · 细分方向(如:具身智能 · 灵巧操作)",
    "series": "每日论文精选",          // 固定不变
    "title_lines": ["第一行","第二行"],  // 2-3 行,做封面大字
    "subtitle": "一句副标题(<=18字,补充封面没说完的具体点)"
  },
  "blocks": [
    // 按顺序排版,前端会自动分页成 3:4。每块尽量短(给手机屏读)。允许的 type:
    {"type":"lead", "text":"开头钩子句(1句,可略吸睛,但说人话不吹)"},
    {"type":"p",    "text":"普通段落"},
    {"type":"num",  "text":"① 或 · 开头的要点/数据行,可含 **强调**"},
    {"type":"sec",  "text":"🔧 小节标题(带一个 emoji)"},
    {"type":"li",   "text":"· 小节下的要点行"},
    {"type":"card", "rows":["论文名 ｜ 机构（国家）","🔗 arxiv.org/abs/xxxx"]},
    {"type":"tags", "items":["具身智能","人形机器人","..."]}   // 6-9 个,不带 # 号
  ]
}

【封面标题铁律(最重要,反复改直到达标)】
title_lines = **一句话总结这篇最核心的贡献**:让一个没读过的人一眼就懂——
  (A) 这是什么领域/什么任务/对什么对象(灵巧手抓取?人形全身控制?世界模型?数据采集?…必须看得出);
  (B) 它新做到了什么/比以前强在哪(那个"成果/能力",不是手段)。
公式:「(领域/任务/对象) + (新实现的能力或更好的结果)」。机制细节(怎么做到的)放进 subtitle,别放标题。

✘ 三类废标题,一律重写:
  1) 只有机制细节、说不清在干嘛:如"只让拇指食指动，其余手指冻结待命"——读者:这啥?什么领域?换来什么?全不知道;
  2) 只有赛道共同目标/愿景:如"零重定向""感知-动作对齐""像人一样灵巧""人动机器人就动"——几十篇都适用,等于没说;
  3) 纯口号无信息:"灵巧操作的新纪元"之类。
✔ 好标题示例:
  · MoDex(序列多物体灵巧抓取):「灵巧手一次抓多个物体，先抓的不松手」(领域=灵巧手抓取,新能力=多物体连抓不掉);
    subtitle 再补机制:「靠手指级动作掩码,给后续抓取预留自由度」;
  · RealDexUMI(灵巧操作数据采集):「采机器人训练数据时，人直接戴上机器人那只手」(领域=数据采集,成果=省掉动作换算);
    subtitle:「采集端与部署端同一型号灵巧手+同构传感」。
写之前先自问:看了这个标题,知道是什么领域吗?知道它实现了什么吗?两个都"是"才合格。

【内容骨架建议(照此组织 blocks)】
  1. lead:一句把这篇最核心的事讲清楚(可略钩);
  2. 痛点:1 个 p + 1-2 个 num,说清它针对什么问题;
  3. sec「🔧 它怎么做的（人话版）」+ 2-3 个 li,把方法讲成人话;
  4. sec「📊 真机/实测结果」+ 2-3 个 num,**只摆材料里真有的数字**(用 **…** 强调关键数值);
  5. sec「⚠️ 论文写明的边界」+ 2-3 个 li,如实列局限(这是事实不是评价);
  6. card:论文名+机构(国家)+arxiv 链接;
  7. tags:6-9 个中文标签。

【强调规则】每个 num/li/p 里,把**关键数字或核心术语**用 **…** 包起来(每块最多 1-2 处),前端会上色。只标真实存在的内容。

严格只输出 JSON,不要 markdown 代码块,所有字段简体中文。"""


def _build_user(pick):
    """拼 LLM 输入。优先用 deep 深析;weekly/论文库无 deep 时,退回平铺字段(claim/方法成分/evidence/verdict)。"""
    d = pick.get("deep", {}) or {}
    method = d.get("method") or " · ".join(pick.get("method_components", []) or [])
    results = d.get("results") or pick.get("evidence", "")
    problem = d.get("problem") or pick.get("claim", "")
    limits = d.get("limitations") or pick.get("reproducibility", "")
    verdict = d.get("verdict") or pick.get("one_sentence_verdict") or pick.get("verdict", "")
    parts = [
        f"标题: {pick.get('title','')}",
        f"机构: {pick.get('org','')}（{pick.get('country','')}）",
        f"arxiv: {pick.get('url','')}",
        f"细分路线(内部): {pick.get('best_route','')} / 领域: {pick.get('domain','')}",
        f"分量分(系统已评): {pick.get('significance','')}/100 — {pick.get('significance_reason','')}",
        f"一句话: {pick.get('tldr','')}",
        f"核心主张: {pick.get('claim','')}",
        f"输入→输出: {pick.get('input','')} → {pick.get('output','')}",
        "",
        "【事实来源(改写它、严禁新增编造)】",
        f"问题/背景: {problem}",
        f"方法: {method}",
        f"结果与证据: {results}",
        f"局限/可复现: {limits}",
        f"时效背景: {d.get('why_now','')}",
        f"一句话判断: {verdict}",
    ]
    return "\n".join([x for x in parts if x.split(': ', 1)[-1].strip() or ':' not in x])


def _load_store():
    if STORE.exists():
        try:
            s = json.loads(STORE.read_text(encoding="utf-8"))
            s.setdefault("by_id", {}); return s
        except Exception:
            pass
    return {"by_id": {}, "latest": ""}


def find_paper(aid):
    """按 arxiv_id 跨 daily_picks / weekly_picks / 论文库 找一篇,返回(来源, paper dict)。"""
    if PICKS.exists():
        arch = json.loads(PICKS.read_text(encoding="utf-8"))
        for dt, lst in (arch.get("picks_by_date") or {}).items():
            for p in lst:
                if p.get("arxiv_id") == aid:
                    return ("daily:" + dt, p)
    if WEEKLY.exists():
        for p in json.loads(WEEKLY.read_text(encoding="utf-8")).get("picks", []):
            if p.get("arxiv_id") == aid:
                return ("weekly", p)
    if DATA.exists():
        for p in json.loads(DATA.read_text(encoding="utf-8")).get("papers", []):
            if p.get("arxiv_id") == aid:
                return ("library", p)
    return (None, None)


def gen_and_store(aid, llm, force=False):
    """生成单篇并写入 xhs_store.json(by_id) + xhs_sample.json。已存在且非 force 则直接复用。"""
    store = _load_store()
    if aid in store["by_id"] and not force:
        xhs = store["by_id"][aid]
        SAMPLE.write_text(json.dumps(xhs, ensure_ascii=False, indent=2), encoding="utf-8")
        return xhs, "cached"
    src, p = find_paper(aid)
    if not p:
        raise ValueError(f"库里找不到论文 {aid}")
    xhs = _gen_one(p, llm)
    if not xhs:
        raise ValueError("LLM 生成失败(检查 key/网络)")
    store["by_id"][aid] = xhs
    store["latest"] = aid
    STORE.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")
    SAMPLE.write_text(json.dumps(xhs, ensure_ascii=False, indent=2), encoding="utf-8")
    return xhs, src


def _gen_one(pick, llm):
    spec = analyze._OPENAI_COMPAT.get(llm.get("provider", "qwen"))
    if not spec:
        print("  provider 不支持,跳过"); return None
    key = analyze._resolve_key(spec["key_envs"])
    if not key:
        print("  未配置 key,跳过"); return None
    try:
        from openai import OpenAI
    except ImportError:
        print("  缺 openai 包,跳过"); return None
    base_url = llm.get("base_url") or spec["base_url"]
    try:
        client = OpenAI(api_key=key, base_url=base_url)
        resp = client.chat.completions.create(
            model=llm.get("model", "qwen-plus"),
            max_tokens=2600, temperature=0.5,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": SYSTEM},
                      {"role": "user", "content": _build_user(pick)}])
        data = analyze._parse_json(resp.choices[0].message.content)
        if not data.get("cover") or not data.get("blocks"):
            print("  LLM 输出缺字段,跳过"); return None
        # 保底:series 固定、thumb 透传(前端封面用)
        data["cover"]["series"] = "每日论文精选"
        data["arxiv_id"] = pick.get("arxiv_id")
        data["thumb"] = pick.get("thumb", "")
        return data
    except Exception as e:
        print(f"  生成失败: {e}"); return None


def llm_config():
    cfg = config.load_config()
    llm = cfg.get("daily_pick", {}) or cfg.get("llm", {})   # 复用精选/全局 LLM 配置
    return {"provider": llm.get("provider", "qwen"),
            "model": llm.get("model", "qwen-plus"),
            "base_url": llm.get("base_url")}


def main():
    args = sys.argv[1:]
    want_id = args[args.index("--id") + 1] if "--id" in args else None
    want_date = args[args.index("--date") + 1] if "--date" in args else None
    do_all = "--all" in args
    force = "--force" in args
    llm = llm_config()

    # --id:跨 daily/weekly/库 生成单篇(详情页按钮走的就是这条路,无需 date)
    if want_id:
        xhs, src = gen_and_store(want_id, llm, force=force)
        print(f"[{src}] {want_id} → cover='{'/'.join(xhs['cover'].get('title_lines', []))}'  blocks={len(xhs['blocks'])}")
        print(f"已写 {STORE.name}(by_id) + {SAMPLE.name}")
        return

    # --all / 默认:对 daily 精选批量(主要给冷启动/补全用)
    if not PICKS.exists():
        print("daily_picks.json 不存在,先跑 pick_daily.py"); return
    arch = json.loads(PICKS.read_text(encoding="utf-8"))
    pbd = arch.get("picks_by_date", {})
    flat = [(dt, p) for dt in sorted(pbd) for p in pbd[dt]
            if (want_date is None or dt == want_date)]
    if do_all:
        targets = flat
    else:
        latest = want_date or arch.get("latest") or (sorted(pbd)[-1] if pbd else None)
        day = [(dt, p) for dt, p in flat if dt == latest]
        targets = [max(day, key=lambda x: x[1].get("significance", 0))] if day else []
    if not targets:
        print("没找到目标 pick"); return

    done = skipped = 0
    for dt, p in targets:
        aid = p.get("arxiv_id")
        try:
            _, src = gen_and_store(aid, llm, force=force)
            if src == "cached":
                skipped += 1
            else:
                done += 1; print(f"  ✓ [{dt}] {p.get('title','')[:46]}")
        except Exception as e:
            print(f"  ✗ [{dt}] {aid}: {e}")
    print(f"完成:新生成 {done} 篇,跳过(已存在) {skipped} 篇 → {STORE.name}")


if __name__ == "__main__":
    main()
