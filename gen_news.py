#!/usr/bin/env python3
"""企业/基模动态 RSS 活水:抓 Google News RSS(query 驱动,可靠免key)→ 每日最新动态 news.json。
让「动态」板块从调研快照变每日更新。无额外依赖(urllib + ElementTree)。
"""
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path(__file__).resolve().parent / "docs" / "news.json"
GN = "https://news.google.com/rss/search?q={q}&hl=zh-CN&gl=CN&ceid=CN:zh"

# 每个领域几条 query(可随时增删 = 常更新)
QUERIES = {
    "embodied": ["人形机器人", "具身智能 融资", "宇树 OR 智元 OR 银河通用", "Figure OR Tesla Optimus robot"],
    "bci": ["脑机接口", "Neuralink OR Synchron", "脑虎 OR 博睿康"],
    "llm": ["大模型 发布", "GPT OR Claude OR Gemini 发布", "DeepSeek OR Qwen OR Kimi"],
}


def fetch(q):
    url = GN.format(q=urllib.parse.quote(q))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 robot-intel"})
        raw = urllib.request.urlopen(req, timeout=20).read()
        root = ET.fromstring(raw)
    except Exception as e:
        print(f"  [{q}] 失败: {e}")
        return []
    out = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        src = it.find("{http://www.w3.org/2005/Atom}source")
        source = (it.findtext("source") or (src.text if src is not None else "") or "").strip()
        out.append({
            "title": title,
            "link": (it.findtext("link") or "").strip(),
            "date": (it.findtext("pubDate") or "")[:16],
            "source": source,
        })
    return out[:6]


def main():
    news = []
    seen = set()
    for dom, qs in QUERIES.items():
        for q in qs:
            for item in fetch(q):
                key = item["title"][:40]
                if not item["title"] or key in seen:
                    continue
                seen.add(key)
                item["domain"] = dom
                news.append(item)
            time.sleep(1)   # 礼貌
    OUT.write_text(json.dumps({"generated_at": "2026-06-03", "news": news},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    from collections import Counter
    print(f"news.json: {len(news)} 条", dict(Counter(n["domain"] for n in news)))


if __name__ == "__main__":
    main()
