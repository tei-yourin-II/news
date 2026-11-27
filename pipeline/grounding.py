"""数字核对:LLM 写的"最硬结果"里出现的每个数字,都必须能在原文(正文或摘要)里找到,
否则整句作废。起因:让模型凭已有拆解补写结果句时,它会编出看起来很像样的数字
(如把 WER 6.9% 写成 18.7%)。提示词管不住,只能程序核对。"""
import re

_NUM = re.compile(r"\d+(?:[.,]\d+)*")


def _norm(text):
    return re.sub(r"(?<=\d),(?=\d{3})", "", text or "")


def numbers(text):
    return [n.rstrip(".") for n in _NUM.findall(_norm(text))]


def grounded(claim, source):
    """claim 里的数字是否都出现在 source 里。没有数字的句子视为通过。"""
    src = _norm(source)
    for n in numbers(claim):
        if len(n) == 1 and "." not in n:      # 个位数太常见,不查
            continue
        if not re.search(r"(?<![\d.])" + re.escape(n) + r"(?!\d)", src):
            return False
    return True


def scrub(analysis, source):
    """原地核对 headline_result / takeaway:数字对不上的,结果句清空、要点句打标。返回作废了几处。"""
    bad = 0
    if analysis.get("headline_result") and not grounded(analysis["headline_result"], source):
        analysis["_headline_rejected"] = analysis["headline_result"]
        analysis["headline_result"] = ""
        bad += 1
    if analysis.get("takeaway") and not grounded(analysis["takeaway"], source):
        analysis["_takeaway_rejected"] = analysis["takeaway"]
        analysis["takeaway"] = ""
        bad += 1
    return bad
