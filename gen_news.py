#!/usr/bin/env python3
"""企业/基模动态 RSS 活水:抓 Google News RSS(query 驱动,可靠免key)→ 每日最新动态 news.json。
让「动态」板块从调研快照变每日更新。无额外依赖(urllib + ElementTree)。

按「地区(region)」分组抓:中国走 CN 端点、日本走 JP 端点(日文 query)、欧美走 US 端点。
每条 news 带 region 字段(cn/jp/us/global),供独立的《业界新闻》页(news.html)按地区筛选/分栏。
"""
import json
import time
import urllib.parse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path(__file__).resolve().parent / "docs" / "news.json"

# 各地区的 Google News 端点参数(语言/国家/版本),决定返回结果的语种与地域口径
ENDPOINTS = {
    "cn": "hl=zh-CN&gl=CN&ceid=CN:zh",
    "jp": "hl=ja&gl=JP&ceid=JP:ja",
    "us": "hl=en-US&gl=US&ceid=US:en",
}
GN = "https://news.google.com/rss/search?q={q}&{ep}"

# 领域 → 地区 → 几条 query(可随时增删 = 常更新)。
# jp 用日文关键词命中本土媒体/厂商;us 用英文做欧美与全球面;cn 保留原有中文口径。
QUERIES = {
    "embodied": {
        "cn": ["人形机器人", "具身智能 融资", "宇树 OR 智元 OR 银河通用"],
        "jp": [
            "ヒューマノイド ロボット",
            "人型ロボット 開発",
            "トヨタ OR ソニー OR 川崎重工 ロボット",
            "Preferred Networks OR ファナック OR 安川電機 ロボット",
            "テレイグジスタンス OR GROOVE X OR サイバーダイン",
        ],
        "us": ["humanoid robot funding", "Figure OR Tesla Optimus OR Boston Dynamics"],
    },
    "bci": {
        "cn": ["脑机接口", "脑虎 OR 博睿康"],
        "jp": [
            "ブレインマシンインターフェース",
            "BMI 脳 研究 日本",
            "脳科学 ニューラリンク",
        ],
        "us": ["brain computer interface Neuralink OR Synchron"],
    },
    "llm": {
        "cn": ["大模型 发布", "DeepSeek OR Qwen OR Kimi"],
        "jp": [
            "生成AI 国産LLM",
            "Sakana AI OR ELYZA OR rinna 言語モデル",
            "NTT tsuzumi OR NEC 生成AI",
        ],
        "us": ["OpenAI OR Anthropic OR Google DeepMind model release"],
    },
}


def fetch(q, region):
    url = GN.format(q=urllib.parse.quote(q), ep=ENDPOINTS[region])
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 robot-intel"})
        raw = urllib.request.urlopen(req, timeout=20).read()
        root = ET.fromstring(raw)
    except Exception as e:
        print(f"  [{region}/{q}] 失败: {e}")
        return []
    out = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        src = it.find("{http://www.w3.org/2005/Atom}source")
        source = (it.findtext("source") or (src.text if src is not None else "") or "").strip()
        pub = (it.findtext("pubDate") or "").strip()
        out.append({
            "title": title,
            "link": (it.findtext("link") or "").strip(),
            "date": pub[:16],
            "ts": _to_ts(pub),   # 可排序时间戳(ISO),供前端按最新排序
            "source": source,
            "region": region,
        })
    return out[:6]


def _to_ts(pub):
    """RFC822 pubDate → ISO 字符串(可字典序排序);解析失败回退空串。"""
    try:
        return parsedate_to_datetime(pub).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M")
    except Exception:
        return ""


def main():
    news = []
    seen = set()
    for dom, by_region in QUERIES.items():
        for region, qs in by_region.items():
            for q in qs:
                for item in fetch(q, region):
                    key = item["title"][:40]
                    if not item["title"] or key in seen:
                        continue
                    seen.add(key)
                    item["domain"] = dom
                    news.append(item)
                time.sleep(1)   # 礼貌
    news.sort(key=lambda n: n.get("ts", ""), reverse=True)  # 最新在前
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    OUT.write_text(json.dumps({"generated_at": today, "news": news},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    from collections import Counter
    print(f"news.json: {len(news)} 条",
          "domain=", dict(Counter(n["domain"] for n in news)),
          "region=", dict(Counter(n["region"] for n in news)))


if __name__ == "__main__":
    main()
