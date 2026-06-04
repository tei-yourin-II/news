#!/usr/bin/env python3
"""robot-intel 主流程:
arXiv 拉取 → 相关度过滤 → 质量/热度信号 → LLM 拆解打分 → 写状态 → 导出 dashboard → (可选)推 Notion

每一步都做了优雅降级:没装 ML 库走关键词,没配 key 出占位,单源失败不阻断。
本地跑:  python run.py
"""
import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")  # 静音 HF tokenizers fork 警告

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from pipeline import (analyze, config, export, fetch_openalex, notion_sync,
                      prefilter, quality, relevance, scoring, signals, store)


def main():
    cfg = config.load_config()
    routes = config.enabled_routes(cfg)
    print(f"启用路线: {[r['id'] for r in routes]}")

    # 1) 抓候选论文(OpenAlex 锁 arXiv 源做主力 + HF Daily 兜底,失败不崩)
    ac = cfg["arxiv"]
    oc = cfg.get("openalex", {})
    try:
        papers = _gather_candidates(ac, oc)
        print(f"候选论文共 {len(papers)} 篇(已合并去重)")
    except Exception as e:
        print(f"抓取失败,跳过本次新增: {e}")
        _finish(store.load(), routes)
        return
    if not papers:
        print("没抓到候选,跳过。")
        _finish(store.load(), routes)
        return

    # 2) 去重(跳过已处理过的)
    state = store.load()
    seen = store.seen_ids(state)
    papers = [p for p in papers if p["arxiv_id"] not in seen]
    print(f"其中新论文 {len(papers)} 篇")
    if not papers:
        _finish(state, routes)
        return

    # 3) 相关度过滤
    profiles = relevance.build_profiles(routes)
    papers, backend = relevance.score_papers(
        papers, profiles, anchor_terms=ac.get("search_terms"))
    print(f"相关度后端: {backend}")
    fc = cfg["filter"]
    papers.sort(key=lambda p: p["relevance_raw"], reverse=True)
    pf = cfg.get("prefilter", {})
    if pf.get("enabled"):
        # 锚点门(score_papers 已把域外压到 ≤0.05)后,交 LLM 做精筛 + 分路线
        cand = [p for p in papers if p["relevance_raw"] >= 0.06][:pf.get("max_candidates", 150)]
        verdicts = prefilter.classify(cand, routes, pf, pf.get("batch_size", 40))
        survivors = []
        for p in cand:
            v = verdicts.get(p["arxiv_id"], {})
            if not v.get("relevant"):
                continue
            if v.get("route"):                       # 用 LLM 判的路线(比嵌入 argmax 准)
                p["best_route"] = v["route"]
                rs = p.setdefault("route_scores", {})
                rs[v["route"]] = max(rs.get(v["route"], 0.0), 0.5)
            survivors.append(p)
        print(f"锚点门 → {len(cand)} 候选; LLM 初筛 → {len(survivors)} 相关")
        survivors = survivors[:fc["keep_top_k"]]
    else:
        survivors = [p for p in papers if p["relevance_raw"] >= fc["relevance_min"]][:fc["keep_top_k"]]
    print(f"进入深拆解 → {len(survivors)} 篇")

    # 4) 信号 + LLM 拆解 + 打分
    hf_up = signals.fetch_hf_upvotes()
    weights = cfg["scoring"]["weights"]
    gt, pt = cfg["scoring"]["grade_thresholds"], cfg["scoring"]["priority_thresholds"]
    llm_cfg = cfg["llm"]
    max_llm = llm_cfg.get("max_papers_per_run", 30)

    # 给每篇贴上"该领域基石参照"(校准 significance:相对 RT-2/DreamZero 等是什么水平)
    anchors = _load_anchors(routes)
    for p in survivors:
        a = anchors.get(p.get("best_route"))
        if a:
            p["_anchors"] = a

    # LLM 拆解:并行调用(DashScope 支持并发,40 篇从串行几分钟压到几十秒)
    to_llm = survivors[:max_llm]
    with ThreadPoolExecutor(max_workers=6) as ex:
        analyses = list(ex.map(lambda p: analyze.analyze(p, llm_cfg), to_llm))
    print(f"  LLM 并行拆解 {len(to_llm)} 篇完成")
    for p in survivors:
        p.pop("_anchors", None)  # 临时字段,别写进 store

    records = []
    for i, p in enumerate(survivors):
        a = analyses[i] if i < len(to_llm) else analyze._stub(p)
        up = p.get("hf_upvotes") or hf_up.get(p["arxiv_id"], 0)
        heat01 = signals.heat_score(up)
        # 引用数:OpenAlex 已白送 cited_by_count → 直接用(免 S2 调用);新论文通常≈0,
        # 靠下面每日 _refresh 随论文变老再补。无该字段(HF 兜底来的)则 0。
        cites = p.get("cited_by_count", 0)
        quality01 = quality.quality_score({"citations": cites}) if cites else 0.0
        sc = scoring.compute(p, a, heat01, quality01, weights)
        p["analysis"] = a
        p["signals"] = {"hf_upvotes": up, "citations": cites, "venue": ""}
        p["scores"] = sc
        p["grade"] = scoring.grade(sc["total"], gt)
        p["read_priority"] = scoring.priority(sc["base"], pt)
        records.append(p)
        print(f"  [{i+1}/{len(survivors)}] {p['grade']}/{p['read_priority']} "
              f"{sc['total']:.0f}分 {p['title'][:60]}")

    # 4.5) 刷新老论文的免费信号(热度/引用),让 bonus 随时间长上来。
    #      只重算信号 + 总分,不重跑贵的 LLM(复用已存的 content/analysis)。
    refreshed = _refresh_recent(state, hf_up, weights, gt, pt, days=30, cap=40)
    if refreshed:
        print(f"刷新了 {refreshed} 篇老论文的热度/质量")

    # 5) 持久化 + 导出 + Notion
    store.upsert(state, records)
    store.save(state)
    _finish(state, routes)
    notion_sync.sync(records)
    print(f"完成。新增 {len(records)} 篇,库内共 {len(state['papers'])} 篇。")


def _load_anchors(routes):
    """从 docs/progress.json 读各领域基石,构建 {route_id: 锚点参照串}。
    用于校准新论文的 significance(相对基石定位,而非凭空打分)。"""
    import json
    from pathlib import Path
    pj = Path(__file__).resolve().parent / "docs" / "progress.json"
    if not pj.exists():
        return {}
    try:
        topics = json.loads(pj.read_text(encoding="utf-8")).get("topics", {})
    except Exception:
        return {}
    # 每个 topic 的 top 基石 → 一段参照文本
    topic_str = {}
    for tid, t in topics.items():
        works = sorted(t.get("works", []), key=lambda w: -(w.get("significance") or 0))[:8]
        if works:
            topic_str[tid] = "; ".join(f"{w['name']}={w.get('significance')}" for w in works)
    # route → topic:同名优先,否则按 domain 兜底
    by_domain = {}
    for tid, t in topics.items():
        by_domain.setdefault(t.get("domain"), tid)
    out = {}
    for r in routes:
        rid, dom = r["id"], r.get("domain", "embodied_ai")
        tid = rid if rid in topic_str else by_domain.get(dom)
        if tid and tid in topic_str:
            out[rid] = topic_str[tid]
    return out


def _gather_candidates(ac, oc):
    """组装候选池,按 arxiv_id 去重。两源:
       a) OpenAlex 锁 arXiv 源(关键词×日期检索)—— 主力,为轮询而生,实测无 429,顺带拿被引用;
       b) HF Daily Papers 直取全字段 —— 兜底,自带社区热度。
    (arXiv 老 API export.arxiv.org/api/query 从云 IP 几乎必 429,已退役。)
    """
    terms = ac.get("search_terms") or []
    by_id = {}

    # a) OpenAlex —— 主力,失败不致命交给 HF 兜底
    if oc.get("enabled", True):
        try:
            since = (datetime.now(timezone.utc)
                     - timedelta(days=oc.get("days", 7))).strftime("%Y-%m-%d")
            oa = fetch_openalex.fetch_recent(
                terms, oc.get("source_id", "S4306400194"), since,
                oc.get("mailto", ""), oc.get("per_page", 200),
                oc.get("terms_per_query", 12), oc.get("max_pages", 2))
            for p in oa:
                by_id[p["arxiv_id"]] = p
            print(f"  OpenAlex 锁 arXiv 源检索 → {len(oa)} 篇")
        except Exception as e:
            print(f"  OpenAlex 抓取失败(跳过,靠 HF 兜底): {e}")

    # b) HF Daily Papers —— 兜底,直接拿全字段元数据
    if ac.get("use_hf_daily"):
        hf = signals.fetch_hf_papers()
        added = 0
        for p in hf:
            if p["arxiv_id"] not in by_id:
                by_id[p["arxiv_id"]] = p
                added += 1
        print(f"  HF Daily Papers 直取 → {len(hf)} 篇(新增 {added})")

    return list(by_id.values())


def _refresh_recent(state, hf_up, weights, gt, pt, days=30, cap=40):
    """给近 N 天的老论文重算热度/质量信号 + 总分(不动 LLM 拆解)。"""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = [p for p in state.get("papers", [])
              if (p.get("published", "")[:10] >= cutoff) and p.get("analysis")]
    recent = recent[:cap]
    n = 0
    for p in recent:
        q = quality.fetch_quality(p["arxiv_id"])
        up = hf_up.get(p["arxiv_id"], p.get("signals", {}).get("hf_upvotes", 0))
        heat01 = signals.heat_score(up)
        quality01 = quality.quality_score(q)
        sc = scoring.compute(p, p["analysis"], heat01, quality01, weights)
        p["signals"] = {"hf_upvotes": up, "citations": q["citations"], "venue": q["venue"]}
        p["scores"] = sc
        p["grade"] = scoring.grade(sc["total"], gt)
        p["read_priority"] = scoring.priority(sc["base"], pt)
        n += 1
    return n


def _finish(state, routes):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out = export.export(state, routes, now)
    print(f"已导出 dashboard 数据 → {out}")


if __name__ == "__main__":
    main()
