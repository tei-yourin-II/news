"""质量/影响力信号的 0~1 映射(引用/venue)。
引用数/venue 由 OpenAlex 白送(取数与每日刷新都从 fetch_openalex 拿,见 run.py),
不再调 Semantic Scholar —— 省掉逐篇限流。新论文引用≈0 属正常,随论文变老每天重算会长上来。"""
import math


# 顶会/顶刊关键词 → 给 venue 一点加成
TOP_VENUES = ["neurips", "icml", "iclr", "cvpr", "iccv", "eccv", "corl",
              "rss", "icra", "iros", "acl", "emnlp", "siggraph", "nature", "science"]


def quality_score(q):
    cites = math.log1p(q.get("citations", 0)) / math.log1p(500)
    infl = math.log1p(q.get("influential_citations", 0)) / math.log1p(50)
    venue_low = (q.get("venue") or "").lower()
    venue_boost = 0.25 if any(v in venue_low for v in TOP_VENUES) else 0.0
    return min(0.6 * cites + 0.3 * infl + venue_boost, 1.0)
