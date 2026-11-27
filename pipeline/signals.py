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


def hot_votes(upvotes=0, stars=0, cites=0, venue="", award=""):
    """把各路关注度折成「等效票数」V(系数在 agent/weights.yaml):
    HF 点赞、GitHub star、被引、顶会录用、口头/亮点/最佳论文。
    只用 HF 点赞会漏掉大半个机器人圈(很多好论文根本不上 HF 每日榜)。"""
    from .weights import load
    w = load()["votes"]
    v = w["hf_upvote"] * (upvotes or 0) + w["github_star"] * (stars or 0) + w["citation"] * (cites or 0)
    if award:
        v += w["awards"].get(award, 0)
    elif venue:
        v += w["venue_accept"]
    return v


def hot_score(upvotes=0, stars=0, cites=0, venue="", award=""):
    """关注度 H = scale·log2(1 + V/half),不封顶(默认 25 和 10:票数每翻一倍 +25,
    10 票=25,70=75,150=100,630=150)。100 是"很热"的刻度而不是天花板。"""
    from .weights import load
    h = load()["heat"]
    return round(h["scale"] * math.log2(1 + hot_votes(upvotes, stars, cites, venue, award) / h["half"]), 1)


def fetch_hf_by_ids(ids, workers=6):
    """逐篇查 HF 论文页(没上每日榜的论文也可能有点赞和登记的仓库)。
    返回 {arxiv_id: {...}},HF 上没有这篇的不在结果里。"""
    from concurrent.futures import ThreadPoolExecutor

    def one(aid):
        try:
            req = urllib.request.Request(f"https://huggingface.co/api/papers/{aid}",
                                         headers={"User-Agent": "robot-intel/0.1"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                d = json.loads(resp.read())
            return aid, {"upvotes": d.get("upvotes") or 0, "stars": d.get("githubStars") or 0,
                         "comments": d.get("numComments") or 0, "repo": d.get("githubRepo") or "",
                         "project": d.get("projectPage") or ""}
        except Exception:
            return aid, None
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return {a: v for a, v in ex.map(one, ids) if v}


_REPO = __import__("re").compile(r"github\.com/([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)")


def find_repo(*texts):
    """从 comment / 摘要里抠第一个 GitHub 仓库地址(owner/repo)。"""
    for t in texts:
        m = _REPO.search(t or "")
        if m:
            owner, repo = m.group(1), m.group(2).rstrip(".").removesuffix(".git")
            if owner.lower() not in ("orgs", "topics", "features") and repo:
                return f"https://github.com/{owner}/{repo}"
    return ""


def fetch_github_stars(repos, token="", workers=6):
    """{repo_url: (stars, created_at)}。有 token(GITHUB_TOKEN/GH_TOKEN)额度 5000/时;没有只有 60/时,只查前 50 个。
    created_at 用来判断这个仓库是不是这篇论文自己的(见 refresh_heat)。"""
    from concurrent.futures import ThreadPoolExecutor
    repos = list(dict.fromkeys(r for r in repos if r))
    if not token:
        repos = repos[:50]

    def one(url):
        m = _REPO.search(url)
        if not m:
            return url, None
        h = {"User-Agent": "robot-intel/0.1", "Accept": "application/vnd.github+json"}
        if token:
            h["Authorization"] = f"Bearer {token}"
        try:
            req = urllib.request.Request(f"https://api.github.com/repos/{m.group(1)}/{m.group(2)}", headers=h)
            with urllib.request.urlopen(req, timeout=20) as resp:
                d = json.loads(resp.read())
                return url, (d.get("stargazers_count", 0), (d.get("created_at") or "")[:10])
        except Exception:
            return url, None
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return {u: s for u, s in ex.map(one, repos) if s is not None}
