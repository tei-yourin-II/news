#!/usr/bin/env python3
"""事后验证:回看 N 天前入库的论文,当时的内容排名有没有说中后来的关注度。

"后来的关注度"只取入库之后才会慢慢长出来的信号:被引、GitHub star、会议录用/获奖
(HF 点赞主要发生在头几天,不算"后来")。给编辑 agent 调权重用——没有对错标准的
自我迭代只会越调越像自己的口味。

输出 agent/retro_latest.md。  用法: python retro.py [--min-age 30] [--max-age 90]
注意:同批强制排名 2026-11-13 才开始;更早的档位是旧分量分按当月名次换算的(表里标"换算")。
"""
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline import config, rank, signals, store

OUT = Path(__file__).resolve().parent / "agent" / "retro_latest.md"


def _arg(flag, default):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def later(p):
    """入库后才累积的等效票数(不含 HF 点赞)。"""
    s = p.get("signals", {}) or {}
    return signals.hot_votes(0, s.get("github_stars", 0), s.get("citations", 0),
                             p.get("venue") or s.get("venue", ""), p.get("award", ""))


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    if len(xs) < 3:
        return float("nan")
    rx, ry = ranks(xs), ranks(ys)
    mx, my = st.mean(rx), st.mean(ry)
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / den if den else float("nan")


def main():
    cfg = config.load_config()
    lo, hi = int(_arg("--min-age", 30)), int(_arg("--max-age", 90))
    now = datetime.now(timezone.utc)
    d_new = (now - timedelta(days=lo)).strftime("%Y-%m-%d")
    d_old = (now - timedelta(days=hi)).strftime("%Y-%m-%d")
    dom = {r["id"]: r.get("domain", "embodied_ai") for r in cfg["routes"]}
    state = store.load()
    store._calibrate(state)
    ps = [p for p in state["papers"]
          if d_old <= (p.get("first_seen") or p.get("published") or "")[:10] <= d_new
          and p.get("rank") and p.get("source") not in ("cornerstone", "conference")]
    L = [f"# 事后验证 {now:%Y-%m-%d}", "",
         f"样本:入库 {hi}~{lo} 天前的论文 {len(ps)} 篇。"
         f"其中真正同批排名的 {sum(1 for p in ps if not p['rank'].get('legacy'))} 篇,"
         f"其余档位由旧分量分换算。", "",
         "后来的关注度 = 被引×系数 + star×系数 + 会议/奖项加成(不含 HF 点赞),系数见 agent/weights.yaml。", ""]
    for d in ("embodied_ai", "bci", "ai_science"):
        sub = [p for p in ps if dom.get(p.get("best_route"), "embodied_ai") == d]
        if len(sub) < 20:
            continue
        ys = [later(p) for p in sub]
        top = sorted(ys, reverse=True)[max(1, len(ys) // 10) - 1]
        L += [f"## {d}({len(sub)} 篇)", "",
              f"内容分与后来关注度的秩相关 ρ = {spearman([rank.merit(p) for p in sub], ys):.2f}"
              f";HF 点赞(头几天就定型)与后来关注度 ρ = "
              f"{spearman([(p.get('signals') or {}).get('hf_upvotes', 0) or 0 for p in sub], ys):.2f}", "",
              "| 档位 | 篇数 | 后来有任何信号的占比 | 后来关注度中位数 | 进后来前 10% 的占比 |", "|---|---|---|---|---|"]
        for t in ("S", "A", "B"):
            g = [later(p) for p in sub if p["rank"]["tier"] == t]
            if g:
                L.append(f"| {t} | {len(g)} | {sum(1 for y in g if y > 0) / len(g):.0%} | {st.median(g):.1f} | "
                         f"{sum(1 for y in g if y >= top and y > 0) / len(g):.0%} |")
        miss = sorted((p for p in sub if p["rank"]["tier"] == "B"), key=later, reverse=True)[:8]
        L += ["", "**当时排在 B、后来关注度最高的(漏判)**", ""]
        L += [f"- {later(p):.0f} 票 · {p['arxiv_id']} · {p['title'][:70]}"
              f"(引 {p['signals'].get('citations', 0)} / ★ {p['signals'].get('github_stars', 0)} / {p.get('award') or p.get('venue') or '-'})"
              for p in miss if later(p) > 0]
        fa = [p for p in sub if p["rank"]["tier"] == "S" and later(p) == 0]
        L += ["", f"**当时排在 S、至今没有任何后续信号的:{len(fa)} 篇**(列前 8)", ""]
        L += [f"- {p['arxiv_id']} · {p['title'][:70]}" for p in fa[:8]]
        # 哪些可观察特征和后来的关注度有关(给调权重找抓手)
        L += ["", "**按特征分组的后来关注度中位数 / 有信号占比**", ""]
        for key in ("reproducibility", "sim2real_status", "org_type"):
            groups = defaultdict(list)
            for p in sub:
                groups[str((p.get("analysis") or {}).get(key, ""))[:24]].append(later(p))
            row = " ; ".join(f"{k or '空'}: {st.median(v):.0f} / {sum(1 for y in v if y > 0) / len(v):.0%}(n={len(v)})"
                             for k, v in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:6] if len(v) >= 8)
            L.append(f"- {key} → {row}")
        L.append("")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:60]))


if __name__ == "__main__":
    main()
