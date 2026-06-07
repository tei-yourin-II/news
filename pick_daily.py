#!/usr/bin/env python3
"""今日精选:时效性内容流的发动机。

区别于论文库(significance 降序、不衰减,回答"全时代最强"):精选只看「时效窗内」的
新论文,每日严选 1-3 篇,做「人能读、可搬运社媒」的深度解析(回答"今天值得读什么")。

机制(对齐 config.daily_pick):
  1. 候选 = 指定领域(当前只具身) + first_seen(无则 published 兜底)在 window_days 内;
  2. 选片 = significance(挑剔标尺)主导 + base/heat/venue 轻加权;过 sig_floor 才够格,
            按 pick_score 取 max_picks 篇。当日不足 min_picks → 从近 fallback_days
            「从未精选过」的里放宽到 sig_floor_fallback 补;仍没有则当天不出(不为凑数降质);
  3. 深析 = 只对选中的 1-3 篇跑长文 LLM 解读(硬核技术+可搬运两立),复用已抓 teaser 图;
  4. 沉淀 = 按日期 append-only 写 docs/daily_picks.json(往期精选可回看),记 featured_ids 防重复。

幂等:同一天已有精选则跳过(--force 重抽当天)。
用法: python pick_daily.py [--force]
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline import analyze, config, store

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "daily_picks.json"


DEEP_SYSTEM = """你是顶尖的具身智能/机器人方向论文解读者,给一篇「当日精选」论文写深度解析。
读者是关注具身智能的工程师与研究者,也要让认真的爱好者读懂——所以**硬核但讲人话**:
技术上准确、挑剔(必须点出局限与存疑,不替作者吹),同时可读性强、结构清楚,能直接当社媒长文发出去。

⚠️ 全部字段用简体中文。不要写"这篇论文很有前景/值得关注"这种空话,要具体、可判断、有信息量。
⚠️ 严禁编造数字:只能引用摘要里**明确出现**的数值/指标/数据集名;摘要没给的成功率、提升幅度、对比倍数、指标名一律不要瞎编(这是要发出去的内容,编造数字=翻车)。摘要没数就定性描述(如"作者报告在真机上显著提升",别伪造百分比)。

只输出一个 JSON 对象:
{
  "hook": "一句话亮点/钩子(<=40字,适合做标题或开头,点出这篇最爽的点)",
  "why_now": "为什么现在值得读(时效角度:它接续/推翻了哪些近期工作,踩中什么趋势)",
  "problem": "它要解决的问题与背景(讲清痛点,2-4句)",
  "method": "怎么做的(把核心方法讲成人话,关键创新点说透,2-5句)",
  "results": "关键结果与证据(挑实证:真机/多任务/消融/SOTA幅度;有数就摆数)",
  "limitations": "局限与存疑(挑剔!纯仿真?小数据?没消融?泛化存疑?复现难?至少2点)",
  "significance_take": "对该路线意味着什么(放进领域脉络:增量 / 显著推进 / 范式级,并说理由)",
  "who_should_read": "谁该读、读了能拿走什么(一句)",
  "verdict": "一句犀利总评(给明确态度:必读/值得读/可略读,并说为什么)"
}
严格只输出 JSON,不要 markdown 代码块。"""


def _deep_read(paper, dp_cfg):
    """对选中的精选论文跑长文深度解析。复用 analyze 的 provider/key 约定;不可用则返回 None(降级)。"""
    provider = dp_cfg.get("provider", "qwen")
    spec = analyze._OPENAI_COMPAT.get(provider)
    if not spec:
        return None
    key = analyze._resolve_key(spec["key_envs"])
    if not key:
        print("  [deep] 未配置 key,跳过深析(出占位)")
        return None
    try:
        from openai import OpenAI
    except ImportError:
        return None
    base_url = dp_cfg.get("base_url") or spec["base_url"]
    a = paper.get("analysis", {}) or {}
    user = (f"标题: {paper['title']}\n\n"
            f"机构: {a.get('org', '')} ({a.get('country', '')})\n"
            f"分量分(系统已评): {a.get('significance', '')}/100 — {a.get('significance_reason', '')}\n"
            f"一句话: {a.get('tldr', '')}\n"
            f"核心主张: {a.get('claim', '')}\n"
            f"输入→输出: {a.get('input', '')} → {a.get('output', '')}\n"
            f"方法成分: {', '.join(a.get('method_components', []))}\n"
            f"sim2real: {a.get('sim2real_status', '')} | 可复现: {a.get('reproducibility', '')}\n\n"
            f"摘要: {paper.get('abstract', '')}")
    venue = paper.get("venue")
    if venue:
        user = f"【{venue} 论文,顶会接收是强质量信号】\n" + user
    try:
        client = OpenAI(api_key=key, base_url=base_url)
        resp = client.chat.completions.create(
            model=dp_cfg.get("model", "qwen-plus"),
            max_tokens=2048, temperature=0.4,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": DEEP_SYSTEM},
                      {"role": "user", "content": user}])
        data = analyze._parse_json(resp.choices[0].message.content)
        data["_llm"] = dp_cfg.get("model")
        return data
    except Exception as e:
        print(f"  [deep] 解析失败,跳过: {e}")
        return None


def _date_key(p):
    """时效基准:first_seen(入库日)优先,无则用 published 日期。"""
    return p.get("first_seen") or (p.get("published") or "")[:10]


def _sig(p):
    return (p.get("analysis", {}) or {}).get("significance", 0) or 0


def _pscore(p):
    """选片分:significance(挑剔标尺)主导,base(今日读价值)/heat(热度)/venue 轻加权。"""
    s = p.get("scores", {}) or {}
    venue_bonus = 6 if p.get("venue") else 0
    return _sig(p) + 0.25 * (s.get("base", 0) or 0) + 0.5 * (s.get("heat", 0) or 0) + venue_bonus


def _pick_obj(p, deep, domain):
    a = p.get("analysis", {}) or {}
    sig = _sig(p)
    tier = "heavy" if sig >= 75 else "notable" if sig >= 60 else "worth"
    return {
        "arxiv_id": p["arxiv_id"], "title": p["title"],
        "published": (p.get("published") or "")[:10],
        "first_seen": p.get("first_seen", ""),
        "url": p.get("url"), "pdf_url": p.get("pdf_url"),
        "thumb": p.get("thumb", ""), "venue": p.get("venue", ""),
        "domain": domain, "best_route": p.get("best_route"),
        "org": a.get("org", ""), "country": a.get("country", ""),
        "significance": sig, "significance_reason": a.get("significance_reason", ""),
        "tier": tier, "tldr": a.get("tldr", ""),
        "deep": deep or {},   # 深度解析(空 = LLM 降级时的占位)
    }


def _load_archive():
    if OUT.exists():
        try:
            d = json.loads(OUT.read_text(encoding="utf-8"))
            d.setdefault("picks_by_date", {})
            d.setdefault("featured_ids", [])
            return d
        except Exception:
            pass
    return {"picks_by_date": {}, "featured_ids": [], "latest": ""}


def _save_archive(d):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    force = "--force" in sys.argv
    cfg = config.load_config()
    dp = cfg.get("daily_pick", {})
    if not dp.get("enabled", True):
        print("daily_pick 未启用,跳过。")
        return

    domains = set(dp.get("domains", ["embodied_ai"]))
    route_dom = {r["id"]: r.get("domain", "embodied_ai") for r in cfg["routes"]}
    dom_of = lambda p: route_dom.get(p.get("best_route"), "embodied_ai")

    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    archive = _load_archive()
    if today in archive["picks_by_date"] and not force:
        n = len(archive["picks_by_date"][today])
        print(f"今日 {today} 已有精选({n} 篇),跳过(--force 重抽)。")
        return

    papers = [p for p in store.load().get("papers", []) if dom_of(p) in domains]
    # 已精选集合从历史推导(排除今天自身,这样 --force 重抽当天不会把今天的选择当成"已精选"剔掉)
    featured = {pk["arxiv_id"] for dt, lst in archive["picks_by_date"].items()
                if dt != today for pk in lst}

    floor = dp.get("sig_floor", 60)
    max_picks = dp.get("max_picks", 3)
    min_picks = dp.get("min_picks", 1)
    win_cut = (now - timedelta(days=dp.get("window_days", 2))).strftime("%Y-%m-%d")

    # 1) 当日时效窗内、过质量地板、未精选过的候选
    fresh = [p for p in papers
             if _date_key(p) >= win_cut and _sig(p) >= floor and p["arxiv_id"] not in featured]
    fresh.sort(key=_pscore, reverse=True)
    picks = fresh[:max_picks]

    # 2) 不足 min_picks → 从近 fallback_days「未精选过」里放宽地板补(仍守质量底线)
    if len(picks) < min_picks:
        fb_cut = (now - timedelta(days=dp.get("fallback_days", 7))).strftime("%Y-%m-%d")
        fb_floor = dp.get("sig_floor_fallback", 55)
        chosen = {p["arxiv_id"] for p in picks}
        pool = [p for p in papers
                if _date_key(p) >= fb_cut and _sig(p) >= fb_floor
                and p["arxiv_id"] not in featured and p["arxiv_id"] not in chosen]
        pool.sort(key=_pscore, reverse=True)
        need = min_picks - len(picks)
        added = pool[:need]
        picks += added
        print(f"  当日窗内达标 {len(fresh)} 篇 < 保底 {min_picks},fallback 补 {len(added)} 篇")

    if not picks:
        print(f"今日 {today} 时效窗({win_cut}起)内无达标论文(地板 sig≥{floor}),"
              f"当天不出(不为凑数降质)。")
        return

    print(f"今日精选 {len(picks)} 篇:")
    for p in picks:
        print(f"  sig={_sig(p):>3} score={_pscore(p):5.1f} {p['title'][:58]}")

    # 3) 深度解析(只对选中的 1-3 篇,成本极低)
    out_picks = [_pick_obj(p, _deep_read(p, dp), dom_of(p)) for p in picks]

    # 4) 沉淀:append-only by date + 累积 featured_ids 防重复
    archive["picks_by_date"][today] = out_picks
    archive["featured_ids"] = sorted(featured | {p["arxiv_id"] for p in picks})  # 含今天,供查阅
    archive["latest"] = today
    archive["generated_at"] = now.strftime("%Y-%m-%d %H:%M UTC")
    _save_archive(archive)
    print(f"已写 {OUT}(往期共 {len(archive['picks_by_date'])} 天精选)")


if __name__ == "__main__":
    main()
