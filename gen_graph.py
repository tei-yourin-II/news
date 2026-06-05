#!/usr/bin/env python3
"""知识图谱 阶段1:从论文库已有字段 + 本地嵌入相似度,建多类型知识图谱 → docs/graph.json。
节点:论文 / 机构 / 国家 / 路线。
边:论文—机构(by)、机构—国家(in)、论文—路线(route)、论文—相似论文(similar,嵌入top-k)。
零新基建;嵌入用 sentence-transformers(没装则跳过相似边)。
"""
import json
import re
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

from pipeline import config, entities, store

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
    node_by = {}                       # id -> node dict(便于回填 count)
    org_papers = Counter()             # canonical org -> 论文数(节点权重)
    collab = Counter()                 # frozenset({orgA,orgB}) -> 共同论文数

    def add_node(nid, **attr):
        if nid not in seen:
            seen.add(nid)
            n = {"id": nid, **attr}
            nodes.append(n)
            node_by[nid] = n
        return node_by[nid]

    for p in papers:
        a = p.get("analysis", {})
        pid = p["arxiv_id"]
        dom = route_dom.get(p.get("best_route"), "embodied_ai")
        add_node(pid, type="paper", label=p["title"], domain=dom,
                 sig=a.get("significance", 0), country=_clean(a.get("country")))
        rid = p.get("best_route")
        if rid:
            add_node("route:" + rid, type="route", label=route_name.get(rid, rid), domain=route_dom.get(rid, "embodied_ai"))
            links.append({"source": pid, "target": "route:" + rid, "type": "route"})

        # —— 实体归一:一条 org 串 → 多个规范机构,每个连一条 by 边(复合机构=合作)——
        resolved = entities.resolve(a.get("org"))
        canon_orgs = []
        for canon, co in resolved:
            oid = "org:" + canon
            add_node(oid, type="org", label=canon, country=co, domain=dom)
            links.append({"source": pid, "target": oid, "type": "by"})
            org_papers[oid] += 1
            canon_orgs.append(oid)
            if co and co != "unknown":
                add_node("co:" + co, type="country", label=co)
                links.append({"source": oid, "target": "co:" + co, "type": "in"})
        # 同一篇论文的多机构 → 两两合作边(权重=共同论文数)
        for x, y in combinations(sorted(set(canon_orgs)), 2):
            collab[frozenset((x, y))] += 1

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

    # —— 机构↔机构 合作边(共著论文数为权重)——
    for pair, w in collab.items():
        a, b = tuple(pair)
        links.append({"source": a, "target": b, "type": "collab", "w": w})
    # 机构节点权重 = 论文数(驱动前端节点大小/标签显示)
    for oid, n in org_papers.items():
        if oid in node_by:
            node_by[oid]["count"] = n

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    OUT.write_text(json.dumps({"generated_at": today, "nodes": nodes, "links": links},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"graph.json: {len(nodes)} 节点 {len(links)} 边")
    print("  节点类型:", dict(Counter(n["type"] for n in nodes)))
    print("  边类型:", dict(Counter(l["type"] for l in links)))


if __name__ == "__main__":
    main()
