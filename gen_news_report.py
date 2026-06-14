#!/usr/bin/env python3
"""业界动态 日报 / 周报:把 news.json 的当日/近7天动态,聚合成一篇**可发小红书的速报**。

为什么聚合而不是单条:一条 RSS 只有标题+外链,料太薄、硬写易编造;把当天/一周的动态
按地区(日本优先)、领域聚类成一篇,料足且标题本身就是事实,符合「不编造」铁律。

产物:docs/news_reports.json
  {
    "daily":  { "2026-06-13": <report>, ... },   # 按日存档,留存
    "weekly": { "2026-06-08": <report>, ... },    # 按「周一」存档,留存
    "latest_daily": "2026-06-13", "latest_weekly": "2026-06-08", "generated_at": "..."
  }
report 用与小红书一致的 {cover, blocks} 结构(前端可直接渲染/复制文案),另带 sources 溯源。

用法:
  python gen_news_report.py            # 日报(今天)+ 若今天是周一则同时出周报
  python gen_news_report.py --daily
  python gen_news_report.py --weekly
  python gen_news_report.py --force    # 已存在也重生成
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline import analyze, config

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
NEWS = DOCS / "news.json"
OUT = DOCS / "news_reports.json"

KEEP_DAILY = 60      # 日报最多留近 60 天
KEEP_WEEKLY = 26     # 周报最多留近半年

REGION_NAME = {"jp": "🇯🇵 日本", "cn": "🇨🇳 中国", "us": "🇺🇸 欧美 / 全球"}
REGION_ORDER = ["jp", "cn", "us"]   # 日本优先
DOMAIN_NAME = {"embodied": "具身智能", "bci": "脑机接口", "llm": "大模型基座"}


SYSTEM = """你是具身智能/脑机接口/大模型方向的行业编辑。我给你**当日(或本周)一批真实新闻标题 + 媒体源 + 地区/领域**,
你把它们聚合改写成一篇**适合发小红书的「行业速报」**,只输出一个 JSON 对象。

【铁律】
1. 严禁编造:你只能**复述、归并、提炼我给的标题里已有的信息**。标题里没有的数字、结论、评价一律不准加。
2. 不下主观判断:禁止"突破/颠覆/碾压/里程碑/必读"之类词,客观陈述"谁做了什么"。吸睛只允许出现在封面标题。
3. 每条动态末尾用括号标注媒体源,如「(日経クロステック)」。日文标题可保留原文或简洁意译,但不得改变事实。
4. 按**地区分节,日本放最前**;同地区内可再按领域(具身/脑机/基模)归类。相似的多条可合并成一条并列出多个源。

【输出 JSON 结构】
{
  "cover": {
    "tag": "行业速报 · 具身/脑机/基模",
    "series": "每日行业速报",            // 由我传入覆盖,你按我给的写
    "title_lines": ["第一行","第二行"],   // 2-3 行封面大字:概括今天/本周最值得说的 1-2 件事(必须是给定标题里真有的)
    "subtitle": "一句副标题(<=20字)"
  },
  "blocks": [
    {"type":"lead", "text":"开头一句:今天/本周动态的概览(说人话,不吹)"},
    {"type":"sec",  "text":"🇯🇵 日本"},                       // 地区小节标题(带国旗 emoji)
    {"type":"li",   "text":"· 一条动态的客观一句话 **关键词加粗**(媒体源)"},
    {"type":"li",   "text":"· 下一条…(媒体源)"},
    {"type":"sec",  "text":"🇨🇳 中国"},
    {"type":"li",   "text":"· …(媒体源)"},
    {"type":"sec",  "text":"🇺🇸 欧美 / 全球"},
    {"type":"li",   "text":"· …(媒体源)"},
    {"type":"tags", "items":["人形机器人","脑机接口","..."]}   // 6-9 个中文标签,不带 # 号
  ]
}

【强调规则】每个 li 里把**公司名/关键术语/真实数字**用 **…** 包起来(每条最多 1-2 处,只标真有的)。
日本节尽量充实(这是本号重点)。严格只输出 JSON,不要 markdown 代码块,所有解说用简体中文。"""


def _load_news():
    if not NEWS.exists():
        raise SystemExit("缺 docs/news.json,先跑 gen_news.py")
    return json.loads(NEWS.read_text(encoding="utf-8")).get("news", [])


def _load_out():
    if OUT.exists():
        try:
            d = json.loads(OUT.read_text(encoding="utf-8"))
            d.setdefault("daily", {}); d.setdefault("weekly", {}); return d
        except Exception:
            pass
    return {"daily": {}, "weekly": {}, "latest_daily": "", "latest_weekly": ""}


def _region(n):
    r = n.get("region")
    return r if r in REGION_NAME else "us"


def _window(news, start_date):
    """取 ts 日期 >= start_date(含)的动态,按地区→领域→时间整理。"""
    out = [n for n in news if (n.get("ts") or n.get("date") or "")[:10] >= start_date]
    out.sort(key=lambda n: n.get("ts", ""), reverse=True)
    return out


def _build_user(items, period_label, kind):
    lines = [f"时段: {period_label}({'日报' if kind=='daily' else '周报'}) · 共 {len(items)} 条\n"]
    by_region = {r: [] for r in REGION_ORDER}
    for n in items:
        by_region[_region(n)].append(n)
    for r in REGION_ORDER:
        sub = by_region[r]
        if not sub:
            continue
        lines.append(f"\n【{REGION_NAME[r]}】({len(sub)} 条)")
        for n in sub[:24]:   # 每地区上限,防过长
            dom = DOMAIN_NAME.get(n.get("domain"), "")
            lines.append(f"- [{dom}] {n.get('title','').strip()} —— 源:{n.get('source','')}")
    return "\n".join(lines)


def _gen(items, period_label, kind, series):
    if len(items) < 3:
        print(f"  {kind} 动态太少({len(items)} 条),跳过")
        return None
    spec = analyze._OPENAI_COMPAT.get(CFG["provider"])
    if not spec:
        print("  provider 不支持,跳过"); return None
    key = analyze._resolve_key(spec["key_envs"])
    if not key:
        print("  未配置 key,跳过"); return None
    try:
        from openai import OpenAI
    except ImportError:
        print("  缺 openai 包,跳过"); return None
    client = OpenAI(api_key=key, base_url=CFG["base_url"] or spec["base_url"])
    sysmsg = SYSTEM.replace("每日行业速报", series)
    try:
        resp = client.chat.completions.create(
            model=CFG["model"], max_tokens=3000, temperature=0.4,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": sysmsg},
                      {"role": "user", "content": _build_user(items, period_label, kind)}])
        data = analyze._parse_json(resp.choices[0].message.content)
    except Exception as e:
        print(f"  生成失败: {e}"); return None
    if not data.get("cover") or not data.get("blocks"):
        print("  LLM 输出缺字段,跳过"); return None
    data["cover"]["series"] = series
    data["sources"] = [{"title": n.get("title", ""), "source": n.get("source", ""),
                        "region": _region(n), "domain": n.get("domain", ""),
                        "link": n.get("link", "")} for n in items]
    return data


def _today():
    """以 news.json 的 generated_at 为准(GitHub Action 跑的当天),回退 UTC 今天。"""
    try:
        g = json.loads(NEWS.read_text(encoding="utf-8")).get("generated_at")
        if g:
            return datetime.strptime(g, "%Y-%m-%d").date()
    except Exception:
        pass
    return datetime.now(timezone.utc).date()


def gen_daily(force=False):
    out = _load_out()
    today = _today()
    key = today.isoformat()
    if key in out["daily"] and not force:
        print(f"  日报 {key} 已存在(--force 重生成)"); return out
    news = _load_news()
    items = _window(news, (today - timedelta(days=1)).isoformat())   # 含昨天,容 RSS 时差
    items = [n for n in items if (n.get("ts") or "")[:10] <= key] or items
    label = f"{today.month}月{today.day}日"
    rep = _gen(items, label, "daily", "每日行业速报")
    if not rep:
        return out
    rep.update(kind="daily", date=key, period_label=label,
               generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M"))
    out["daily"][key] = rep
    out["latest_daily"] = key
    _prune(out["daily"], KEEP_DAILY)
    _save(out)
    print(f"  ✓ 日报 {key}:{len(items)} 条 → {' / '.join(rep['cover'].get('title_lines', []))}")
    return out


def gen_weekly(force=False):
    out = _load_out()
    today = _today()
    monday = today - timedelta(days=today.weekday())   # 本周一
    key = monday.isoformat()
    if key in out["weekly"] and not force:
        print(f"  周报 {key} 已存在(--force 重生成)"); return out
    news = _load_news()
    items = _window(news, (today - timedelta(days=6)).isoformat())   # 近 7 天
    sunday = monday + timedelta(days=6)
    label = f"{monday.month}月{monday.day}日–{sunday.month}月{sunday.day}日"
    rep = _gen(items, label, "weekly", "每周行业周报")
    if not rep:
        return out
    rep.update(kind="weekly", date=key, period_label=label,
               generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M"))
    out["weekly"][key] = rep
    out["latest_weekly"] = key
    _prune(out["weekly"], KEEP_WEEKLY)
    _save(out)
    print(f"  ✓ 周报 {label}:{len(items)} 条 → {' / '.join(rep['cover'].get('title_lines', []))}")
    return out


def _prune(d, keep):
    for k in sorted(d.keys(), reverse=True)[keep:]:
        d.pop(k, None)


def _save(out):
    out["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M")
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


def _cfg():
    cfg = config.load_config()
    llm = cfg.get("daily_pick", {}) or cfg.get("llm", {})
    return {"provider": llm.get("provider", "qwen"),
            "model": llm.get("model", "qwen-plus"),
            "base_url": llm.get("base_url")}


CFG = None


def main():
    global CFG
    config.load_env()
    CFG = _cfg()
    args = sys.argv[1:]
    force = "--force" in args
    do_daily = "--daily" in args or not any(a in args for a in ("--daily", "--weekly"))
    do_weekly = "--weekly" in args
    # 默认编排:每天出日报;若今天是周一,顺带出周报
    if not any(a in args for a in ("--daily", "--weekly")):
        do_weekly = _today().weekday() == 0
    if do_daily:
        gen_daily(force=force)
    if do_weekly:
        gen_weekly(force=force)


if __name__ == "__main__":
    main()
