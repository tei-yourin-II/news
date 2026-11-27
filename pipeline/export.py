"""生成 dashboard 的 docs/data.json:论文 + 路线 + 图的边(节点+边,给关系图)。"""
import json
from pathlib import Path

from datetime import datetime, timedelta, timezone

from pipeline import entities, rank

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "data.json"
RECENT_DAYS = 30


def export(state, routes, generated_at):
    papers = state.get("papers", [])
    _dom = {r["id"]: r.get("domain", "embodied_ai") for r in routes}
    rank.calibrate_legacy(papers, lambda p: _dom.get(p.get("best_route"), "embodied_ai"))

    route_meta = {r["id"]: r for r in routes}
    route_counts = {}
    edges = []
    for p in papers:
        for rid, sc in (p.get("route_scores") or {}).items():
            # 只给较相关的路线连边,避免图太密
            if sc and sc >= 0.15:
                edges.append({"source": p["arxiv_id"], "target": f"route:{rid}", "weight": round(sc, 3)})
                route_counts[rid] = route_counts.get(rid, 0) + 1

    routes_out = [{
        "id": rid, "name": route_meta.get(rid, {}).get("name", rid),
        "tier": route_meta.get(rid, {}).get("tier", ""),
        "domain": route_meta.get(rid, {}).get("domain", "embodied_ai"),
        "count": route_counts.get(rid, 0),
    } for rid in route_meta]

    rid_domain = {rid: r.get("domain", "embodied_ai") for rid, r in route_meta.items()}
    data = {
        "generated_at": generated_at,
        "count": len(papers),
        "routes": routes_out,
        "edges": edges,
        "papers": [_slim(p, rid_domain) for p in papers],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 首页只需要近期论文:单独导一份小文件先加载(data.json 近 30MB,等它首页要白屏很久)
    cut = (datetime.now(timezone.utc) - timedelta(days=RECENT_DAYS)).strftime("%Y-%m-%d")
    day = lambda p: (p.get("first_seen") or p.get("published") or "")[:10]
    rec = [p for p in data["papers"] if day(p) >= cut and p["source"] not in ("cornerstone", "conference")]
    recent = {"generated_at": generated_at, "days": RECENT_DAYS,
              "latest": max((day(p) for p in rec), default=""),
              "routes": routes_out, "papers": rec}
    with open(OUT.with_name("recent.json"), "w", encoding="utf-8") as f:
        json.dump(recent, f, ensure_ascii=False, separators=(",", ":"))
    return OUT


def _slim(p, rid_domain=None):
    a = p.get("analysis", {})
    rid_domain = rid_domain or {}
    _orgs = list(entities.resolve(a.get("org")))
    best = p.get("best_route")
    novelty = a.get("novelty", 0) or 0
    verdict = a.get("one_sentence_verdict", "")
    sig = a.get("significance", 0) or 0
    # 分量分(挑剔、连续)→ 分档:🔥重磅 / ★显著 / ◆值得看;不再用作者自吹的布尔
    tier = "heavy" if sig >= 75 else "notable" if sig >= 60 else "worth" if sig >= 45 else ""
    return {
        "arxiv_id": p["arxiv_id"], "title": p["title"],
        "authors": p.get("authors", [])[:6], "published": p.get("published", ""),
        "url": p.get("url"), "pdf_url": p.get("pdf_url"),
        "source": p.get("source", "daily"),
        "venue": p.get("venue", ""),
        "award": p.get("award", ""),
        "thumb": p.get("thumb", ""),
        "best_route": best,
        "domain": rid_domain.get(best, "embodied_ai"),
        "routes": [k for k, v in (p.get("route_scores") or {}).items() if v >= 0.15],
        "tags": a.get("tags", []),
        "scores": p.get("scores", {}),
        "grade": p.get("grade"), "read_priority": p.get("read_priority"),
        "tldr": a.get("tldr", ""),
        "org": _orgs[0][0] if _orgs else a.get("org", ""),       # 规范主机构
        "orgs": [o for o, _ in _orgs],                            # 规范全机构(合作)
        "country": _orgs[0][1] if (_orgs and _orgs[0][1] != "unknown") else a.get("country", ""),
        "org_type": a.get("org_type", ""),
        "novelty": novelty,
        "significance": sig,
        "significance_reason": a.get("significance_reason", ""),
        "tier": tier,
        "verdict": verdict,
        "claim": a.get("claim", ""),
        "input": a.get("input", ""), "output": a.get("output", ""),
        "sim2real_status": a.get("sim2real_status", ""),
        "reproducibility": a.get("reproducibility", ""),
        "method_components": a.get("method_components", []),
        "signals": p.get("signals", {}),
        # —— 新排序体系:内容轴(同批强制排名)+ 热度轴(社区)+ 合成 ——
        "first_seen": p.get("first_seen", ""),
        "merit": rank.merit(p), "hot": rank.hot(p), "combo": rank.combo(p),
        "rank_tier": (p.get("rank") or {}).get("tier", ""),
        "rank_why": (p.get("rank") or {}).get("why", ""),
        "rank_legacy": bool((p.get("rank") or {}).get("legacy")),
        "takeaway": a.get("takeaway", ""),
        "headline_result": a.get("headline_result", ""),
        "evidence_facts": a.get("evidence_facts", ""),
        "hype_gap": a.get("hype_gap", ""),
        "fulltext": bool(a.get("_fulltext")),
    }
