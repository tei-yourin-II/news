"""质量/影响力信号:Semantic Scholar Academic Graph(免费,无需 key,有限流)。
取引用数 / venue。新论文引用≈0 属正常,系统每天重算会随时间长上来。
失败则 quality=0,不阻断管线。"""
import json
import math
import time
import urllib.request

S2 = "https://api.semanticscholar.org/graph/v1/paper/arXiv:{aid}?fields=citationCount,influentialCitationCount,venue,publicationVenue"


def fetch_quality(arxiv_id, delay=0.5):
    try:
        url = S2.format(aid=arxiv_id)
        req = urllib.request.Request(url, headers={"User-Agent": "robot-intel/0.1"})
        with urllib.request.urlopen(req, timeout=8) as resp:  # 限流就快速失败,别拖死管线
            d = json.loads(resp.read())
        time.sleep(delay)  # S2 无 key 限流严,温柔点
        return {
            "citations": d.get("citationCount") or 0,
            "influential_citations": d.get("influentialCitationCount") or 0,
            "venue": d.get("venue") or "",
        }
    except Exception:
        return {"citations": 0, "influential_citations": 0, "venue": ""}


# 顶会/顶刊关键词 → 给 venue 一点加成
TOP_VENUES = ["neurips", "icml", "iclr", "cvpr", "iccv", "eccv", "corl",
              "rss", "icra", "iros", "acl", "emnlp", "siggraph", "nature", "science"]


def quality_score(q):
    cites = math.log1p(q.get("citations", 0)) / math.log1p(500)
    infl = math.log1p(q.get("influential_citations", 0)) / math.log1p(50)
    venue_low = (q.get("venue") or "").lower()
    venue_boost = 0.25 if any(v in venue_low for v in TOP_VENUES) else 0.0
    return min(0.6 * cites + 0.3 * infl + venue_boost, 1.0)
