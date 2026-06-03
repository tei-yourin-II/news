"""生成 dashboard 的 docs/data.json:论文 + 路线 + 图的边(节点+边,给关系图)。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "data.json"


def export(state, routes, generated_at):
    papers = state.get("papers", [])

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
    return OUT


def _slim(p, rid_domain=None):
    a = p.get("analysis", {})
    rid_domain = rid_domain or {}
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
        "thumb": p.get("thumb", ""),
        "best_route": best,
        "domain": rid_domain.get(best, "embodied_ai"),
        "routes": [k for k, v in (p.get("route_scores") or {}).items() if v >= 0.15],
        "tags": a.get("tags", []),
        "scores": p.get("scores", {}),
        "grade": p.get("grade"), "read_priority": p.get("read_priority"),
        "tldr": a.get("tldr", ""),
        "org": a.get("org", ""),
        "country": a.get("country", ""),
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
    }
