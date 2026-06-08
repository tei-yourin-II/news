#!/usr/bin/env python3
"""本周具身 Top15:对齐参考图「具身智能一周论文文库」的周报选片器。

区别于 pick_daily(每日 1-3 篇时效流)与论文库(全时代最强):
本脚本按「发表日期落在本周窗口内」选当周最值得读的 N 篇具身论文,产出
目录 + 详情 两段数据(docs/weekly_picks.json),供排版成图。

三条硬规则(对齐需求):
  1. 只具身——按 best_route 的 domain 过滤,排除 ai_science / bci 等;
  2. 综合各大学会——给会议论文配额(venue_quota),顶会先占坑,其余按分填;
  3. 不含旧的——按 published(发表日)卡在本周窗口,天然排除 cornerstone/旧回填。

选片分:significance(挑剔标尺)主导 + base/heat/venue 轻加权(同 pick_daily)。
详情字段直接复用已存的 analysis(claim/method/...),默认不再花钱跑 LLM;
--deep 时对 Top deep_n 篇补长文解析(复用 pick_daily 的深析)。

用法:
  python pick_weekly.py                      # 最近 7 天(到今天)
  python pick_weekly.py --start 2026-06-01 --end 2026-06-07
  python pick_weekly.py --deep              # 额外对 Top N 跑长文深析
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline import config, store

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "weekly_picks.json"


def _arg(flag, default=None):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def _sig(p):
    return (p.get("analysis", {}) or {}).get("significance", 0) or 0


def _pscore(p):
    """选片分:significance 主导,base(读价值)/heat(热度)/venue 轻加权。"""
    s = p.get("scores", {}) or {}
    venue_bonus = 6 if p.get("venue") else 0
    return _sig(p) + 0.25 * (s.get("base", 0) or 0) + 0.5 * (s.get("heat", 0) or 0) + venue_bonus


def _card(p, domain, rank):
    """周报条目:目录字段 + 详情字段(复用 analysis,排版层直接取用)。"""
    a = p.get("analysis", {}) or {}
    sig = _sig(p)
    tier = "heavy" if sig >= 75 else "notable" if sig >= 60 else "worth"
    return {
        "rank": rank,
        "arxiv_id": p["arxiv_id"], "title": p["title"],
        "published": (p.get("published") or "")[:10],
        "url": p.get("url"), "pdf_url": p.get("pdf_url"),
        "thumb": p.get("thumb", ""), "venue": p.get("venue", ""),
        "domain": domain, "best_route": p.get("best_route"),
        "org": a.get("org", ""), "country": a.get("country", ""),
        "org_type": a.get("org_type", ""),
        "significance": sig, "significance_reason": a.get("significance_reason", ""),
        "tier": tier, "grade": p.get("grade", ""),
        "tags": a.get("tags", []),
        # —— 详情卡(对齐参考图「论文详情」的结构化摘要)——
        "tldr": a.get("tldr", ""),
        "claim": a.get("claim", ""),
        "method_components": a.get("method_components", []),
        "input": a.get("input", ""), "output": a.get("output", ""),
        "novelty": a.get("novelty", ""), "evidence": a.get("evidence", ""),
        "one_sentence_verdict": a.get("one_sentence_verdict", ""),
        "deep": p.get("_deep", {}),   # --deep 时填充,否则空
    }


def main():
    cfg = config.load_config()
    wp = cfg.get("weekly_pick", {})
    domains = set(wp.get("domains", ["embodied_ai"]))
    top_n = int(_arg("--top", wp.get("top_n", 15)))
    venue_quota = int(wp.get("venue_quota", 4))
    deep = "--deep" in sys.argv

    route_dom = {r["id"]: r.get("domain", "embodied_ai") for r in cfg["routes"]}
    dom_of = lambda p: route_dom.get(p.get("best_route"), "embodied_ai")

    # 周窗口:--end 默认今天,--start 默认 end 前 6 天(共 7 天)
    end = _arg("--end") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    start = _arg("--start") or (
        datetime.strptime(end, "%Y-%m-%d") - timedelta(days=6)).strftime("%Y-%m-%d")

    papers = store.load().get("papers", [])
    # 规则1+3:只具身 + published 落在本周窗口(自动排除 cornerstone/旧回填)
    pool = [p for p in papers
            if dom_of(p) in domains and start <= (p.get("published") or "")[:10] <= end]
    pool.sort(key=_pscore, reverse=True)
    print(f"本周 {start}~{end} 具身候选:{len(pool)} 篇,选 Top{top_n}(会议配额 {venue_quota})")

    if not pool:
        print("窗口内无具身论文,跳过。")
        return

    # 规则2:会议配额——顶会论文先占 venue_quota 坑,其余按分填满 top_n
    picks, chosen = [], set()
    for p in pool:                       # 先按分扫,挑出会议论文占配额
        if p.get("venue") and len(picks) < venue_quota:
            picks.append(p); chosen.add(p["arxiv_id"])
    for p in pool:                       # 其余名额按分填(会议论文若分高也会在这里再被选)
        if len(picks) >= top_n:
            break
        if p["arxiv_id"] not in chosen:
            picks.append(p); chosen.add(p["arxiv_id"])
    picks.sort(key=_pscore, reverse=True)  # 最终按分排目录序
    picks = picks[:top_n]

    n_venue = sum(1 for p in picks if p.get("venue"))
    print(f"入选 {len(picks)} 篇(其中会议 {n_venue} 篇):")
    for i, p in enumerate(picks, 1):
        vt = f" [{p['venue']}]" if p.get("venue") else ""
        print(f"  {i:2}. sig={_sig(p):>3} {_pscore(p):5.1f} [{p.get('best_route')}]{vt} {p['title'][:52]}")

    if deep:
        from pick_daily import _deep_read
        dp = cfg.get("daily_pick", {})
        deep_n = int(wp.get("deep_n", top_n))
        print(f"  --deep:对 Top{deep_n} 跑长文深析…")
        for p in picks[:deep_n]:
            p["_deep"] = _deep_read(p, dp) or {}

    cards = [_card(p, dom_of(p), i) for i, p in enumerate(picks, 1)]
    out = {
        "week": {"start": start, "end": end, "label": f"{start[5:]}~{end[5:]}".replace("-", ".")},
        "count": len(cards),
        "venue_count": n_venue,
        "venues": sorted({p["venue"] for p in picks if p.get("venue")}),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "picks": cards,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已写 {OUT}(目录+详情 {len(cards)} 篇)")


if __name__ == "__main__":
    main()
