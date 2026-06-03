#!/usr/bin/env python3
"""给库里有真 arxiv_id 的论文抓 teaser 配图(VLM 定位裁剪),留存到 docs/assets/thumbs/。
幂等:已有图的跳过。可随时重跑。按 significance 高的先抓(经典优先)。
"""
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from pipeline import config, export, store, thumbs

ARXIV_RE = re.compile(r"^\d{4}\.\d{4,5}$")
WORKERS = 8


def main():
    cfg = config.load_config()
    routes = config.enabled_routes(cfg)
    state = store.load()
    papers = [p for p in state["papers"] if ARXIV_RE.match(str(p.get("arxiv_id", "")))]
    papers.sort(key=lambda p: -(p.get("analysis", {}).get("significance", 0) or 0))
    todo = [p for p in papers if not p.get("thumb")]
    print(f"待抓图 {len(todo)} 篇(并发 {WORKERS})")
    lock = threading.Lock()
    done = [0]

    def work(p):
        t = thumbs.fetch(p["arxiv_id"])
        with lock:
            done[0] += 1
            if t:
                p["thumb"] = t
            if done[0] % 20 == 0:
                store.save(state)
            print(f"  [{done[0]}/{len(todo)}] {'✓' if t else '–'} {p['arxiv_id']} {p['title'][:40]}")
        return bool(t)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        results = list(ex.map(work, todo))
    store.save(state)
    export.export(state, routes, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    print(f"完成:新增配图 {sum(results)} 篇 / 共处理 {len(todo)}")


if __name__ == "__main__":
    main()
