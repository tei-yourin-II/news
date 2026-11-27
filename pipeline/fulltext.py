"""取论文正文(arXiv PDF → 纯文本),给 LLM 读全文用。
只看摘要时,模型只能复述作者自己的说法;读到实验章节才能核对"说了什么"和"做到了什么"。
拿不到(非 arXiv、下载失败、没装 PyMuPDF)返回 "",调用方退回摘要。"""
import os
import re
import urllib.request
from pathlib import Path

ARXIV_RE = re.compile(r"^\d{4}\.\d{4,5}$")
CACHE = Path(os.environ.get("FULLTEXT_CACHE", "")) if os.environ.get("FULLTEXT_CACHE") else None
_REF = re.compile(r"\n\s*(References|REFERENCES|Bibliography)\s*\n")


def fetch(aid, max_chars=40000):
    if not ARXIV_RE.match(str(aid or "")):
        return ""
    if CACHE and (CACHE / f"{aid}.txt").exists():
        return (CACHE / f"{aid}.txt").read_text(encoding="utf-8")[:max_chars]
    try:
        import fitz
    except ImportError:
        return ""
    try:
        req = urllib.request.Request(f"https://arxiv.org/pdf/{aid}",
                                     headers={"User-Agent": "robot-intel/0.1"})
        pdf = urllib.request.urlopen(req, timeout=40).read()
        doc = fitz.open(stream=pdf, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
    except Exception:
        return ""
    # 参考文献之后的内容(文献列表;附录通常也在其后)对判断没用,截掉
    cuts = [m.start() for m in _REF.finditer(text)]
    if cuts and cuts[-1] > len(text) * 0.3:
        text = text[:cuts[-1]]
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if CACHE:
        CACHE.mkdir(parents=True, exist_ok=True)
        (CACHE / f"{aid}.txt").write_text(text, encoding="utf-8")
    return text[:max_chars]
