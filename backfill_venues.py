#!/usr/bin/env python3
"""会议归属回填:给库里已有、但还没标 venue 的 arXiv 论文补识别。

run.py 从此版本起会在入库时自动识别会议(pipeline/venue.py);但历史论文是
之前入库的,没走过识别。本脚本对「没 venue 的真实 arXiv 论文」批量拉 comment →
正则识别 → 回写 venue + signals.venue,并经 store.upsert 顺带去重。

注意:很多新论文此刻还没被会议接收(comment 里自然没有「Accepted to X」),
命中率低是正常的——它的价值随论文变老、被会议接收后逐周累积。

幂等:已有 venue 的跳过。
用法:
  python backfill_venues.py                 # 默认只回填最近 60 天发表的
  python backfill_venues.py --days 9999     # 全库
"""
import re
import sys

from pipeline import config, fetch_arxiv, store, venue


def _arg(flag, default=None):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def main():
    config.load_config()
    days = int(_arg("--days", 60))
    state = store.load()
    papers = state.get("papers", [])

    from datetime import datetime, timedelta, timezone
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    todo = [p for p in papers
            if not p.get("venue")
            and re.match(r"^\d{4}\.\d{4,5}$", p["arxiv_id"])
            and (p.get("published") or "")[:10] >= cutoff]
    print(f"待回填(近 {days} 天、无 venue、真实 arXiv 号):{len(todo)} 篇")
    if not todo:
        return

    ids = [p["arxiv_id"] for p in todo]
    print("拉 comment 中(arXiv id_list,分批)…")
    comments = fetch_arxiv.fetch_comments(ids)
    print(f"  拿到 comment {len(comments)} 篇")

    hit = 0
    for p in todo:
        v = venue.detect(comments.get(p["arxiv_id"], ""), p.get("abstract", ""))
        if v:
            p["venue"] = v
            p.setdefault("signals", {})["venue"] = v
            a = p.get("analysis")
            if isinstance(a, dict):
                a["venue"] = v
            hit += 1
            print(f"  ✓ [{v}] {p['title'][:60]}")
    print(f"命中会议 {hit} 篇。")

    if hit:
        store.upsert(state, [])   # 触发去重 + 排序(papers 已就地改 venue)
        store.save(state)
        print(f"已写回 data/papers.json(库内共 {len(state['papers'])} 篇)。"
              f"重生成周报请跑 pick_weekly.py。")


if __name__ == "__main__":
    main()
