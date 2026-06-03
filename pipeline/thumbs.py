"""论文配图留存:抓**最能代表核心贡献的那张图**,裁剪后存进 docs/assets/thumbs/。
做法(实测可靠):渲染 PDF 前几页 → 每页问 qwen-vl"本页最核心的配图 + 代表性评分" →
跨页挑评分最高的(架构/总览图得高分,实物照片/小示例得低分)→ 按 0~1 框裁剪。
HF 缩略图(文字)、PyMuPDF 抽嵌入图(蒙版)都不可靠,已弃用。
没装库/没 key/拿不到 → None,不阻断。
"""
import base64
import io
import json
import os
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THUMB_DIR = ROOT / "docs" / "assets" / "thumbs"
ARXIV_RE = re.compile(r"^\d{4}\.\d{4,5}$")
VL_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
PROMPT = ('这是论文某一页截图。找出本页**最能代表论文核心贡献的配图**'
          '(优先 总览图/架构图/方法框图/pipeline/系统图;实物照片、单个定性示例、表格给低分)。'
          '只输出 JSON: {"found":true/false,"box":[x0,y0,x1,y1],"score":0到10}。'
          'box 是该图相对本页宽高的 0~1 归一化坐标;'
          'score 是这张图代表论文核心的程度(架构/总览图≈8-10,普通结果图≈5-7,实物照片/小示例≈1-3)。'
          '本页无明显配图 found=false。')


def _client():
    key = os.environ.get("QWEN_API_KEY") or os.environ.get("DASHSCOPE_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
    except ImportError:
        return None
    return OpenAI(api_key=key, base_url=VL_BASE)


def _norm(box):
    b = box[0] if box and isinstance(box[0], list) else box
    b = [float(x) for x in b]
    if max(b) > 1.5:                       # qwen 有时给 0~1000 或像素,统一回 0~1
        b = [x / 1000.0 for x in b]
    return [max(0.0, min(1.0, x)) for x in b]


def _page_figure(client, png, model):
    """问一页,返回 (score, box0_1) 或 None。"""
    b64 = base64.b64encode(png).decode()
    r = client.chat.completions.create(
        model=model, max_tokens=200,
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
            {"type": "text", "text": PROMPT}]}])
    t = r.choices[0].message.content
    j = json.loads(t[t.find("{"): t.rfind("}") + 1])
    if not j.get("found"):
        return None
    box = _norm(j["box"])
    if box[2] - box[0] < 0.12 or box[3] - box[1] < 0.05:
        return None
    return float(j.get("score", 5)), box


def fetch(aid, model="qwen-vl-max", pages=5, zoom=2.0, delay=0.2):
    """返回 assets/thumbs/<id>.png 或 None。已存在则直接返回。逐页评分,挑最高那张裁剪。"""
    if not ARXIV_RE.match(str(aid or "")):
        return None
    existing = list(THUMB_DIR.glob(f"{aid}.*"))
    if existing:
        return f"assets/thumbs/{existing[0].name}"
    client = _client()
    if client is None:
        return None
    try:
        import fitz
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
    except ImportError:
        return None
    try:
        pdf = urllib.request.urlopen(
            urllib.request.Request(f"https://arxiv.org/pdf/{aid}", headers={"User-Agent": "robot-intel/0.1"}),
            timeout=30).read()
        doc = fitz.open(stream=pdf, filetype="pdf")
    except Exception:
        return None
    best = None
    try:
        for pno in range(min(pages, doc.page_count)):
            pix = doc[pno].get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            png, w, h = pix.tobytes("png"), pix.width, pix.height
            try:
                got = _page_figure(client, png, model)
            except Exception:
                got = None
            time.sleep(delay)
            if got and (best is None or got[0] > best[0]):
                best = (got[0], png, w, h, got[1])
            if best and best[0] >= 9:        # 已找到高分总览图,够了,省后续调用
                break
    finally:
        doc.close()
    if best is None:
        return None
    _, png, w, h, (x0, y0, x1, y1) = best
    crop = Image.open(io.BytesIO(png)).crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))).convert("RGB")
    cw, ch = crop.size
    m = max(cw, ch)
    if m > 800:                                    # 压体积:max 边 ≤800,够清晰又轻
        crop = crop.resize((round(cw * 800 / m), round(ch * 800 / m)), Image.LANCZOS)
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    out = THUMB_DIR / f"{aid}.jpg"
    crop.save(out, "JPEG", quality=88, optimize=True)
    return f"assets/thumbs/{out.name}"
