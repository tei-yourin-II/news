#!/usr/bin/env python3
"""关注度补源(每日跑,在 run.py 之后):只靠 HF 每日榜会把大半个机器人圈记成 0。

对近 N 天的 arXiv 论文补四样:
  1. HF 逐篇查 —— 没上每日榜的论文也可能有点赞、登记了仓库
  2. arXiv comment —— 会议录用 / Oral / Best Paper,以及作者自己贴的 GitHub 仓库
  3. GitHub star —— 仓库来自 HF 登记、comment、摘要
  4. 手工补奖 awards.yaml —— best paper 常在会后公布,作者不改 comment 就抓不到
引用数由 run.py 的每日刷新从 OpenAlex 拿。全部只动 signals / venue / award,不调 LLM。

用法: python refresh_heat.py [--days 90]
"""
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline import config, export, fetch_arxiv, fetch_openalex, rank, signals, store, venue

ARXIV_RE = re.compile(r"^\d{4}\.\d{4,5}$")
ROOT = Path(__file__).resolve().parent


def _arg(flag, default):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def main():
    cfg = config.load_config()
    hc = cfg.get("heat", {})
    days = int(_arg("--days", hc.get("refresh_days", 90)))
    state = store.load()
    cut = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = [p for p in state["papers"]
              if ARXIV_RE.match(str(p.get("arxiv_id", ""))) and (p.get("published") or "")[:10] >= cut
              and p.get("analysis") and p.get("source") not in ("cornerstone",)]
    print(f"关注度补源:近 {days} 天 {len(recent)} 篇")
    for p in recent:
        p.setdefault("signals", {})

    # 1) HF 逐篇(内容分高的先查,封顶 hf_lookup_cap 篇/天)
    cap = int(hc.get("hf_lookup_cap", 1500))
    todo = sorted(recent, key=rank.merit, reverse=True)[:cap]
    hf = signals.fetch_hf_by_ids([p["arxiv_id"] for p in todo])
    print(f"  HF 逐篇:查 {len(todo)},HF 上有 {len(hf)} 篇")
    for p in todo:
        h, s = hf.get(p["arxiv_id"]), p["signals"]
        if not h:
            continue
        s["hf_upvotes"] = max(s.get("hf_upvotes") or 0, h["upvotes"])
        s["github_stars"] = max(s.get("github_stars") or 0, h["stars"])
        s["hf_comments"] = max(s.get("hf_comments") or 0, h["comments"])
        s["repo"] = s.get("repo") or h["repo"]
        s["project"] = s.get("project") or h["project"]

    # 2) arXiv comment:会议 / 奖项 / 仓库
    try:
        comments = fetch_arxiv.fetch_comments([p["arxiv_id"] for p in recent])
    except Exception as e:
        print(f"  comment 拉取失败(跳过这一步): {e}")
        comments = {}
    nv = na = 0
    for p in recent:
        c = comments.get(p["arxiv_id"], "")
        if c and not p.get("venue"):
            v = venue.detect(c, "")
            if v:
                p["venue"] = v; p["signals"]["venue"] = v; nv += 1
        aw = venue.award(c) if p.get("venue") else ""
        if aw and aw != p.get("award"):
            p["award"] = aw; na += 1
        if not p["signals"].get("repo"):
            p["signals"]["repo"] = signals.find_repo(c, p.get("abstract", ""))
    print(f"  comment {len(comments)} 篇:新识别会议 {nv},奖项/口头 {na}")

    # 4) 手工补奖
    af = ROOT / "awards.yaml"
    if af.exists():
        import yaml
        manual = yaml.safe_load(af.read_text(encoding="utf-8")) or {}
        by = {p["arxiv_id"]: p for p in state["papers"]}
        for aid, aw in manual.items():
            if str(aid) in by:
                by[str(aid)]["award"] = aw

    # 3) GitHub star
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    repos = [p["signals"]["repo"] for p in sorted(recent, key=rank.merit, reverse=True) if p["signals"].get("repo")]
    stars = signals.fetch_github_stars(repos, token)
    for p in recent:
        st = stars.get(p["signals"].get("repo", ""))
        if st is not None:
            p["signals"]["github_stars"] = max(p["signals"].get("github_stars") or 0, st)
    print(f"  GitHub:{len(set(repos))} 个仓库,查到 {len(stars)} 个" + ("" if token else "(无 token,只查前 50)"))

    # 5) 引用(run.py 只刷近 45 天;这里把窗口内更老的也补上)
    old = [p for p in recent if (p.get("published") or "")[:10] < (
        datetime.now(timezone.utc) - timedelta(days=45)).strftime("%Y-%m-%d")]
    doi = lambda p: p.get("doi") or f"10.48550/arxiv.{p['arxiv_id']}"
    q = fetch_openalex.fetch_quality_batch([doi(p) for p in old], cfg.get("openalex", {}).get("mailto", ""))
    for p in old:
        if doi(p) in q:
            p["signals"]["citations"] = max(p["signals"].get("citations") or 0, q[doi(p)]["citations"])

    zero = sum(1 for p in recent if rank.hot(p) == 0)
    print(f"  关注度仍为 0 的:{zero}/{len(recent)}")
    store.save(state)
    export.export(state, config.enabled_routes(cfg), datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))


if __name__ == "__main__":
    main()
