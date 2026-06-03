"""把四个维度合成 100 分,给 grade(S/A/B/C/D)和 read_priority(A/B/C/D)。

base  = relevance + content    (最高 60,驱动"今天读不读")
bonus = heat + quality         (最高 40,随时间增长)
total = base + bonus           (驱动 S/A/B/C/D)
冷启动友好:新论文 heat/quality≈0,但靠 relevance+content 仍能拿高 read_priority。
"""


def compute(paper, analysis, heat01, quality01, weights):
    w = weights
    relevance = round(min(paper.get("relevance_raw", 0.0), 1.0) * w["relevance"], 1)

    # content = 新颖(0-10) + 证据(0-12) + 可复现(0-8) = 0-30,再按权重缩放
    content_raw = (analysis.get("novelty", 0)
                   + analysis.get("evidence", 0)
                   + analysis.get("reproducibility_score", 0))
    content = round(content_raw / 30.0 * w["content"], 1)

    heat = round(heat01 * w["heat"], 1)
    quality = round(quality01 * w["quality"], 1)

    base = relevance + content
    bonus = heat + quality
    total = round(base + bonus, 1)
    return {
        "relevance": relevance, "content": content,
        "heat": heat, "quality": quality,
        "base": round(base, 1), "bonus": round(bonus, 1), "total": total,
    }


def grade(total, thresholds):
    if total >= thresholds["S"]: return "S"
    if total >= thresholds["A"]: return "A"
    if total >= thresholds["B"]: return "B"
    if total >= thresholds["C"]: return "C"
    return "D"


def priority(base, thresholds):
    if base >= thresholds["A"]: return "A"
    if base >= thresholds["B"]: return "B"
    if base >= thresholds["C"]: return "C"
    return "D"
