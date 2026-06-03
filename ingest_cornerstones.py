#!/usr/bin/env python3
"""把 docs/progress.json 里的领域基石(深度检索来的标尺论文)灌进论文库,作为主干条目。
   标记 source='cornerstone',与每日新论文同库;每日管线靠去重自动跳过它们(不重复处理)。
   progress.json 更新后可重跑本脚本(幂等:按 id 去重 upsert)。
"""
import json
import re
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

from pipeline import config, scoring, store, export

ROOT = Path(__file__).resolve().parent
PROG = ROOT / "docs" / "progress.json"

# topic → 库内代表路线(embodied 的 topic_id 即 route_id;bci/ai_science 映射到具体路线)
TOPIC_ROUTE = {
    "vla": "vla", "world_model": "world_model", "whole_body_control": "whole_body_control",
    "dexterous_manipulation": "dexterous_manipulation", "sim2real_data": "sim2real_data",
    "hardware_unitree": "hardware_unitree", "bci": "bci_neural_decoding", "ai_science": "protein_ai",
}
ARXIV_RE = re.compile(r"^\d{4}\.\d{4,5}$")


def _route_for(topic_id, work):
    if topic_id == "ai_science":
        blob = (work.get("name", "") + work.get("why", "")).lower()
        if any(k in blob for k in ("genom", "dna", "gene", "rna", "cell", "nucleotide", "evo")):
            return "genomics_ai"
        return "protein_ai"
    return TOPIC_ROUTE.get(topic_id, topic_id)


def _year(w):
    m = re.search(r"(19|20)\d{2}", str(w.get("year", "")))
    return m.group(0) if m else "2023"


def _record(topic_id, route, w, idx):
    aid = str(w.get("arxiv_id") or "").strip()
    real = bool(ARXIV_RE.match(aid))
    if not real:
        aid = f"cs-{topic_id}-{idx}"
    sig = int(w.get("significance") or 0)
    name = w.get("name", "")
    url = (f"https://arxiv.org/abs/{aid}" if real
           else "https://www.google.com/search?q=" + urllib.parse.quote(name))
    return {
        "arxiv_id": aid, "title": name, "authors": [],
        "published": f"{_year(w)}-01-01", "updated": f"{_year(w)}-01-01",
        "url": url, "pdf_url": f"https://arxiv.org/pdf/{aid}" if real else url,
        "best_route": route, "route_scores": {route: 1.0}, "relevance_raw": 1.0,
        "source": "cornerstone",
        "analysis": {
            "tldr": w.get("why", name), "claim": w.get("why", name),
            "org": w.get("org", ""), "country": w.get("country", ""), "org_type": "unknown",
            "significance": sig, "significance_reason": "领域基石/里程碑(深度检索标尺)",
            "novelty": min(10, round(sig / 10)), "evidence": 0, "reproducibility_score": 0,
            "method_components": [], "input": "", "output": "",
            "sim2real_status": "", "reproducibility": "", "tags": ["基石"],
            "one_sentence_verdict": "领域基石", "_llm": "cornerstone",
        },
        "signals": {"hf_upvotes": 0, "citations": 0, "venue": ""},
    }


def main():
    cfg = config.load_config()
    routes = config.enabled_routes(cfg)
    w = cfg["scoring"]["weights"]
    gt, pt = cfg["scoring"]["grade_thresholds"], cfg["scoring"]["priority_thresholds"]
    topics = json.loads(PROG.read_text(encoding="utf-8")).get("topics", {})

    recs, seen = [], set()
    for tid, t in topics.items():
        route = _route_for(tid, {})
        for i, work in enumerate(t.get("works", [])):
            r = _route_for(tid, work)
            rec = _record(tid, r, work, i)
            if rec["arxiv_id"] in seen:
                continue
            seen.add(rec["arxiv_id"])
            sig = rec["analysis"]["significance"]
            # 基石没有热度,质量/内容由分量映射,体现其分量地位
            rel, con = 28.0, min(30.0, round(sig * 0.30, 1))
            qual = min(20.0, round(sig * 0.20, 1))
            sc = scoring.compute(rec, rec["analysis"], 0.0, qual / 20.0, w)
            sc["relevance"], sc["content"], sc["quality"] = rel, con, qual
            sc["base"] = round(rel + con, 1)
            sc["total"] = round(sc["base"] + sc["heat"] + qual, 1)
            rec["scores"] = sc
            rec["grade"] = scoring.grade(sc["total"], gt)
            rec["read_priority"] = scoring.priority(sc["base"], pt)
            recs.append(rec)

    state = store.load()
    before = len(state["papers"])
    store.upsert(state, recs)
    store.save(state)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    export.export(state, routes, now)
    print(f"灌入基石 {len(recs)} 篇;库 {before} → {len(state['papers'])} 篇")
    from collections import Counter
    print("按领域:", dict(Counter(r["best_route"] for r in recs)))


if __name__ == "__main__":
    main()
