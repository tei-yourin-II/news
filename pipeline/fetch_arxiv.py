"""从 arXiv API 拉最近论文。只用标准库(urllib + xml),零额外依赖。"""
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"
API = "https://export.arxiv.org/api/query"


def _get(url, delay, retries=4):
    """带 429 退避的 GET,返回解析后的论文列表。"""
    req = urllib.request.Request(url, headers={"User-Agent": "robot-intel/0.1 (research digest)"})
    backoff = max(delay, 3)
    for attempt in range(retries):
        time.sleep(backoff)  # 礼貌延迟 + 退避
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return _parse(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                backoff *= 2
                print(f"  [arxiv] 429 限流,{backoff}s 后重试 ({attempt+1}/{retries})")
                continue
            raise
        except Exception as e:
            print(f"  [arxiv] 请求失败({attempt+1}/{retries}): {e}")
            backoff *= 2
    return []


def fetch_recent(categories, max_results=200, delay=3, retries=4):
    """返回最近提交的论文列表(按提交时间倒序)。"""
    cat_query = "+OR+".join(f"cat:{c}" for c in categories)
    url = (f"{API}?search_query={cat_query}&start=0&max_results={max_results}"
           f"&sortBy=submittedDate&sortOrder=descending")
    return _get(url, delay, retries)


def fetch_by_terms(terms, categories, max_results=300, delay=3, retries=4):
    """关键词驱动检索:在指定分类里搜命中任一关键词的最新论文。
    比"拉某巨型分类最近 N 篇"召回率高得多 —— 200 篇里大半是相关的,而非噪声。
    query = (cat:.. OR ..) AND (all:"term1" OR all:"term2" ..)
    """
    cat_q = "+OR+".join(f"cat:{c}" for c in categories)
    term_q = "+OR+".join(f"all:%22{urllib.parse.quote(t)}%22" for t in terms)
    search = f"%28{cat_q}%29+AND+%28{term_q}%29"   # %28/%29 = 括号
    url = (f"{API}?search_query={search}&start=0&max_results={max_results}"
           f"&sortBy=submittedDate&sortOrder=descending")
    return _get(url, delay, retries)


def fetch_by_ids(arxiv_ids, delay=3, retries=4, chunk=80):
    """按 arXiv ID 批量拉元数据(给 HF 二级源补全、以后 backfill-seeds 用)。"""
    out = []
    ids = [i for i in arxiv_ids if i]
    for k in range(0, len(ids), chunk):
        batch = ids[k:k + chunk]
        url = f"{API}?id_list={','.join(batch)}&max_results={len(batch)}"
        out.extend(_get(url, delay, retries))
    return out


def fetch_comments(arxiv_ids, delay=3, retries=4, chunk=80):
    """按 arXiv ID 批量取 comment 字段(作者自报的会议归属藏在这里)。
    返回 {arxiv_id: comment}。id_list 小批量,实测不触发 429(同 fetch_by_ids)。"""
    out = {}
    for p in fetch_by_ids(arxiv_ids, delay, retries, chunk):
        c = p.get("comment")
        if c:
            out[p["arxiv_id"]] = c
    return out


def _parse(raw):
    root = ET.fromstring(raw)
    out = []
    for e in root.findall(f"{ATOM}entry"):
        arxiv_url = e.findtext(f"{ATOM}id", "").strip()
        # id 形如 http://arxiv.org/abs/2406.09246v1
        arxiv_id = arxiv_url.rsplit("/", 1)[-1].split("v")[0]
        authors = [a.findtext(f"{ATOM}name", "").strip()
                   for a in e.findall(f"{ATOM}author")]
        cats = [c.get("term") for c in e.findall(f"{ATOM}category")]
        pdf = ""
        for link in e.findall(f"{ATOM}link"):
            if link.get("title") == "pdf":
                pdf = link.get("href", "")
        out.append({
            "arxiv_id": arxiv_id,
            "title": " ".join(e.findtext(f"{ATOM}title", "").split()),
            "abstract": " ".join(e.findtext(f"{ATOM}summary", "").split()),
            "authors": authors,
            "categories": cats,
            "comment": " ".join(e.findtext(f"{ARXIV_NS}comment", "").split()),  # 会议归属常在此
            "published": e.findtext(f"{ATOM}published", ""),
            "updated": e.findtext(f"{ATOM}updated", ""),
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "pdf_url": pdf or f"https://arxiv.org/pdf/{arxiv_id}",
        })
    return out
