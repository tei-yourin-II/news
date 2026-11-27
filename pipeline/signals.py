"""热度信号。Day-1 用 Hugging Face Daily Papers 的 upvote(免费、无需 key)。
失败则 heat=0,不阻断管线。"""
import json
import math
import urllib.request


def fetch_hf_upvotes(limit=200):
    """返回 {arxiv_id: upvotes}。HF daily papers API,无需鉴权。"""
    url = "https://huggingface.co/api/daily_papers"  # 不带参数,返回近期列表
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "robot-intel/0.1"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        out = {}
        for item in data:
            paper = item.get("paper", {})
            aid = paper.get("id") or item.get("id")
            up = paper.get("upvotes") or item.get("upvotes") or 0
            if aid:
                out[str(aid).split("v")[0]] = up
        return out
    except Exception as e:
        print(f"  [signals] HF daily papers 拉取失败(不影响管线): {e}")
        return {}


def fetch_hf_papers(limit=200):
    """直接从 HF Daily Papers 取**全字段**论文记录(标题/摘要/作者/upvotes),
    schema 与 fetch_arxiv 对齐 —— 不依赖 arXiv,是稳定的第二数据源。"""
    url = "https://huggingface.co/api/daily_papers"
    out = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "robot-intel/0.1"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"  [signals] HF 论文拉取失败(不影响管线): {e}")
        return out
    for item in data[:limit]:
        paper = item.get("paper", {}) or {}
        aid = str(paper.get("id") or item.get("id") or "").split("v")[0]
        title = paper.get("title") or item.get("title") or ""
        abstract = paper.get("summary") or item.get("summary") or ""
        if not aid or not title:
            continue
        authors = [a.get("name", "") for a in (paper.get("authors") or []) if a.get("name")]
        pub = paper.get("publishedAt") or item.get("publishedAt") or ""
        out.append({
            "arxiv_id": aid,
            "title": " ".join(title.split()),
            "abstract": " ".join(abstract.split()),
            "authors": authors,
            "categories": [],
            "published": pub,
            "updated": pub,
            "url": f"https://arxiv.org/abs/{aid}",
            "pdf_url": f"https://arxiv.org/pdf/{aid}",
            "hf_upvotes": paper.get("upvotes") or item.get("upvotes") or 0,
            "source": "hf_daily",
        })
    return out


def heat_score(upvotes, github_stars=0):
    """upvote/star → 0~1 的热度。对数标度,避免头部碾压。"""
    raw = math.log1p(upvotes) / math.log1p(200) + math.log1p(github_stars) / math.log1p(5000)
    return min(raw, 1.0)


def fetch_hf_range(days=30, pause=0.15):
    """按日期回拉近 N 天的 HF Daily Papers,返回
    {arxiv_id: {"upvotes","stars","comments","repo","project"}}。
    不带 date 的接口只给当天列表:论文入库时票数还低,之后再也刷不到。
    按日期逐天拉才能拿到「现在」的票数(每天 1 个请求,无需鉴权)。"""
    import time
    from datetime import datetime, timedelta, timezone
    out = {}
    today = datetime.now(timezone.utc).date()
    fails = 0
    for i in range(days + 1):
        day = (today - timedelta(days=i)).isoformat()
        url = f"https://huggingface.co/api/daily_papers?date={day}&limit=100"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "robot-intel/0.1"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        except Exception:
            fails += 1
            continue
        for item in data:
            paper = item.get("paper", {}) or {}
            aid = str(paper.get("id") or "").split("v")[0]
            if not aid:
                continue
            out[aid] = {
                "upvotes": paper.get("upvotes") or 0,
                "stars": paper.get("githubStars") or 0,
                "comments": item.get("numComments") or 0,
                "repo": paper.get("githubRepo") or "",
                "project": paper.get("projectPage") or "",
            }
        time.sleep(pause)
    print(f"  [signals] HF 近 {days} 天回拉 → {len(out)} 篇有社区数据(失败 {fails} 天)")
    return out


def hot_score(upvotes=0, stars=0):
    """社区热度 0~100(对数标度):10 票≈42,50 票≈69,150 票≈88,300 票封顶。
    GitHub star 按 20 星≈1 票折算并入。"""
    return round(100 * min(1.0, math.log1p((upvotes or 0) + (stars or 0) / 20.0) / math.log1p(300)), 1)
