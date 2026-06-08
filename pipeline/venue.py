"""会议识别:从 arXiv comment / 文本里抠出顶会顶刊归属。

为什么需要:主管线走 OpenAlex,它给的 venue 对 arXiv 预印本一律是 "arXiv",
拿不到「录用到 CoRL/RSS/NeurIPS」这种关键信号。而作者几乎都会在 arXiv 的
comment 里写明(如 "Accepted to CoRL 2025", "CVPR 2026 Oral")。
这里用正则把这些"各大学会"识别出来,统一成规范名(含年份),供周报/打分加权。

零依赖,纯正则。识别不到返回 ""。
"""
import re

# 规范名 → 匹配模式(全大小写不敏感;优先长名,避免 "ICRA" 命中 "ICRAwhatever")
# 覆盖具身/机器人 + 视觉 + 机器学习 + NLP 主流顶会顶刊。
_VENUES = [
    # 机器人
    ("CoRL",       r"\bCoRL\b|Conference on Robot Learning"),
    ("RSS",        r"\bRSS\b|Robotics:?\s*Science and Systems"),
    ("ICRA",       r"\bICRA\b|International Conference on Robotics and Automation"),
    ("IROS",       r"\bIROS\b|Intelligent Robots and Systems"),
    ("Humanoids",  r"\bHumanoids\b|Humanoid Robots"),
    ("RA-L",       r"\bRA-?L\b|Robotics and Automation Letters"),
    ("T-RO",       r"\bT-?RO\b|Transactions on Robotics"),
    # 视觉
    ("CVPR",       r"\bCVPR\b|Computer Vision and Pattern Recognition"),
    ("ICCV",       r"\bICCV\b|International Conference on Computer Vision"),
    ("ECCV",       r"\bECCV\b|European Conference on Computer Vision"),
    ("SIGGRAPH",   r"\bSIGGRAPH(?:\s*Asia)?\b"),
    # 机器学习
    ("NeurIPS",    r"\bNeurIPS\b|\bNIPS\b|Neural Information Processing Systems"),
    ("ICLR",       r"\bICLR\b|International Conference on Learning Representations"),
    ("ICML",       r"\bICML\b|International Conference on Machine Learning"),
    ("AAAI",       r"\bAAAI\b"),
    ("IJCAI",      r"\bIJCAI\b"),
    ("CoLLAs",     r"\bCoLLAs\b"),
    ("PPSN",       r"\bPPSN\b|Parallel Problem Solving from Nature"),  # 须在 Nature 之前
    # NLP
    ("ACL",        r"\bACL\b(?!\w)"),
    ("EMNLP",      r"\bEMNLP\b"),
    ("NAACL",      r"\bNAACL\b"),
    # 期刊(只认全名,"Science"/"Nature" 作为裸词太常见,不强认,避免误判)
    ("Sci. Robotics", r"Science Robotics"),
    ("Science",    r"\bScience\b(?=\s*\(|,\s*20\d{2}|\s+\d{3,})"),  # 仅"Science (..." / "Science, 2026" / 带卷号
    ("Nat. Mach. Intell.", r"Nature Machine Intelligence"),
    ("Nat. Methods", r"Nature Methods"),
    ("Nature",     r"(?<!from )\bNature\b(?=\s*\(|,\s*20\d{2})"),  # 排除 "...from Nature"(PPSN)
]
_COMPILED = [(name, re.compile(pat, re.I)) for name, pat in _VENUES]
_YEAR = re.compile(r"\b(20\d{2})\b")
# 录用/口头/亮点等强信号词(comment 里出现说明确实被会议接收,而非只是"投稿格式")
_ACCEPT = re.compile(
    r"accept|camera[- ]?ready|to appear|published|oral|spotlight|highlight|"
    r"best paper|honorable mention|poster|proceedings", re.I)


def detect(comment, abstract=""):
    """从 comment(优先)+ abstract 里识别会议归属。
    返回规范名(可能含年份,如 'CoRL 2025');识别不到返回 ""。

    策略:comment 命中任一会议名即采纳(作者自报,可信度高);
    只在 abstract 命中则要求同时出现录用词,避免把"我们在 CVPR 数据集上测试"误判成会议归属。
    """
    text = (comment or "").strip()
    if text:
        v = _match(text)
        if v:
            return v
    ab = (abstract or "").strip()
    if ab and _ACCEPT.search(ab):
        return _match(ab)
    return ""


def _match(text):
    for name, pat in _COMPILED:
        if pat.search(text):
            ym = _YEAR.search(text)
            return f"{name} {ym.group(1)}" if ym else name
    return ""
