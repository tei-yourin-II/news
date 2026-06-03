#!/usr/bin/env python3
"""知识图谱 阶段1:从论文库已有字段 + 本地嵌入相似度,建多类型知识图谱 → docs/graph.json。
节点:论文 / 机构 / 国家 / 路线。
边:论文—机构(by)、机构—国家(in)、论文—路线(route)、论文—相似论文(similar,嵌入top-k)。
零新基建;嵌入用 sentence-transformers(没装则跳过相似边)。
"""
import json
import re
from pathlib import Path

from pipeline import config, store

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "graph.json"


def _clean(s):
    s = (s or "").strip()
    return "" if re.match(r"^(unknown|未知|n/a|none)$", s, re.I) else s


def main():
    cfg = config.load_config()
    route_name = {r["id"]: r.get("name", r["id"]) for r in cfg["routes"]}
    route_dom = {r["id"]: r.get("domain", "embodied_ai") for r in cfg["routes"]}
    papers = store.load()["papers"]

    nodes, links, seen = [], [], set()

    def add_node(nid, **attr):
        if nid not in seen:
            seen.add(nid)
            nodes.append({"id": nid, **attr})

    for p in papers:
        a = p.get("analysis", {})
        pid = p["arxiv_id"]
        dom = route_dom.get(p.get("best_route"), "embodied_ai")
        add_node(pid, type="paper", label=p["title"], domain=dom,
                 sig=a.get("significance", 0), country=_clean(a.get("country")))
        org, co = _clean(a.get("org")), _clean(a.get("country"))
        rid = p.get("best_route")
        if rid:
            add_node("route:" + rid, type="route", label=route_name.get(rid, rid), domain=route_dom.get(rid, "embodied_ai"))
            links.append({"source": pid, "target": "route:" + rid, "type": "route"})
        if org:
            add_node("org:" + org, type="org", label=org, country=co)
            links.append({"source": pid, "target": "org:" + org, "type": "by"})
            if co:
                add_node("co:" + co, type="country", label=co)
                links.append({"source": "org:" + org, "target": "co:" + co, "type": "in"})

    # 论文—相似论文(同域 top-k 余弦)
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
        m = SentenceTransformer("all-MiniLM-L6-v2")
        texts = [f"{p['title']}. {p.get('analysis', {}).get('tldr', '')}" for p in papers]
        vecs = m.encode(texts, normalize_embeddings=True)
        doms = [route_dom.get(p.get("best_route"), "embodied_ai") for p in papers]
        sim = vecs @ vecs.T
        pair = set()
        for i in range(len(papers)):
            order = np.argsort(-sim[i])
            cnt = 0
            for j in order:
                if j == i or doms[j] != doms[i] or sim[i][j] < 0.55:
                    continue
                key = tuple(sorted((i, int(j))))
                if key in pair:
                    continue
                pair.add(key)
                links.append({"source": papers[i]["arxiv_id"], "target": papers[int(j)]["arxiv_id"],
                              "type": "similar", "w": round(float(sim[i][j]), 2)})
                cnt += 1
                if cnt >= 3:
                    break
        print(f"  相似边 {len(pair)} 条(嵌入)")
    except Exception as e:
        print(f"  跳过相似边(无嵌入库): {e}")

    OUT.write_text(json.dumps({"generated_at": "2026-06-03", "nodes": nodes, "links": links},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    from collections import Counter
    print(f"graph.json: {len(nodes)} 节点 {len(links)} 边")
    print("  节点类型:", dict(Counter(n["type"] for n in nodes)))
    print("  边类型:", dict(Counter(l["type"] for l in links)))


if __name__ == "__main__":
    main()
