#!/usr/bin/env python3
"""会议重磅种子回填:按 arxiv id 精准抓取 CVPR/ICRA 等顶会论文,入库。

为什么需要:daily 管线只抓最近 7 天 + 关键词命中的论文,会漏掉
①跨年的会议重磅(如 CVPR 最佳论文 D4RT,2025-12 发的);②弱关键词命中的(纯 3D 视觉/感知)。
这里读 config.yaml `seeds:`(id+venue),抓真实元数据 → 相关度分路线 → LLM 深拆解
(注入 venue 让 significance 公平体现顶会)→ 打分入库,标 source=conference + venue。

幂等:已在库的 id 跳过(除非 --force 重新拆解)。看到该追的会议论文,往 config seeds 加一行即可。
用法: python backfill_seeds.py [--force]
"""
import sys
from concurrent.futures import ThreadPoolExecutor

from pipeline import (analyze, config, export, fetch_arxiv, quality,
                      relevance, scoring, signals, store)
from datetime import datetime, timezone

import run  # 复用 _load_anchors


def main():
    force = "--force" in sys.argv
    cfg = config.load_config()
    routes = config.enabled_routes(cfg)
    seeds = cfg.get("seeds") or []
    if not seeds:
        print("config 无 seeds,跳过。")
        return

    venue_of = {s["id"]: s.get("venue", "会议论文") for s in seeds}
    state = store.load()
    seen = store.seen_ids(state)
    want = [s["id"] for s in seeds if force or s["id"] not in seen]
    print(f"种子 {len(seeds)} 篇,需回填 {len(want)} 篇(已在库 {len(seeds)-len(want)})")
    if not want:
        return

    # 1) 抓真实元数据(arXiv id_list,小批量不限流)
    papers = fetch_arxiv.fetch_by_ids(want)
    got = {p["arxiv_id"] for p in papers}
    miss = [i for i in want if i not in got]
    if miss:
        print(f"  ⚠️ 这些 id 没抓到(检查 id 是否正确): {miss}")
    if not papers:
        print("一篇都没抓到,退出。")
        return
    print(f"  抓到 {len(papers)} 篇真实元数据")

    # 2) 相关度分路线(顶会论文也要落到具体路线)
    profiles = relevance.build_profiles(routes)
    papers, backend = relevance.score_papers(
        papers, profiles, anchor_terms=cfg["arxiv"].get("search_terms"))

    # 3) LLM 深拆解(注入 venue + 基石参照)
    anchors = run._load_anchors(routes)
    for p in papers:
        p["_venue"] = venue_of.get(p["arxiv_id"], "会议论文")
        a = anchors.get(p.get("best_route"))
        if a:
            p["_anchors"] = a
    llm_cfg = cfg["llm"]
    with ThreadPoolExecutor(max_workers=6) as ex:
        analyses = list(ex.map(lambda p: analyze.analyze(p, llm_cfg), papers))
    for p in papers:
        p.pop("_anchors", None)
        p.pop("_venue", None)

    # 4) 打分入库(标 source=conference + venue;顶会给质量信号底)
    weights = cfg["scoring"]["weights"]
    gt, pt = cfg["scoring"]["grade_thresholds"], cfg["scoring"]["priority_thresholds"]
    hf_up = signals.fetch_hf_upvotes()
    records = []
    for p, a in zip(papers, analyses):
        up = hf_up.get(p["arxiv_id"], 0)
        heat01 = signals.heat_score(up)
        cites = p.get("cited_by_count", 0)
        # 顶会接收本身是质量信号:无引用时给个 0.5 底,别让重磅论文 quality=0
        quality01 = quality.quality_score({"citations": cites}) if cites else 0.5
        sc = scoring.compute(p, a, heat01, quality01, weights)
        venue = venue_of.get(p["arxiv_id"], "会议论文")
        a["venue"] = venue
        p["analysis"] = a
        p["source"] = "conference"
        p["venue"] = venue
        p["signals"] = {"hf_upvotes": up, "citations": cites, "venue": venue}
        p["scores"] = sc
        p["grade"] = scoring.grade(sc["total"], gt)
        p["read_priority"] = scoring.priority(sc["base"], pt)
        records.append(p)
        print(f"  [{venue}] sig={a.get('significance',0)} {p['grade']} {p['title'][:55]}")

    store.upsert(state, records)
    store.save(state)
    export.export(state, routes, datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    print(f"完成。回填 {len(records)} 篇,库内共 {len(state['papers'])} 篇。"
          f"(图谱/全景请跑 gen_graph.py 重建)")


if __name__ == "__main__":
    main()
