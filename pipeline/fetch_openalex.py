#!/usr/bin/env python3
"""OpenAlex 取数:锁定 arXiv 源(source S4306400194)做关键词×日期检索。
arXiv 老 API(export.arxiv.org/api/query)从云 IP 几乎必 429;OpenAlex 是为轮询而生的开放目录,
带 mailto 进礼貌池后实测无 429,且白送 abstract / 被引用数 / 机构。

输出 schema 与 fetch_arxiv._parse 完全对齐(arxiv_id/title/abstract/authors/categories/
published/updated/url/pdf_url),多带一个 cited_by_count(可喂 quality)。
零额外依赖(urllib + json)。
"""
import json
import re
import time
import urllib.parse
import urllib.request

API = "https://api.openalex.org/works"
ARXIV_DOI = re.compile(r"arxiv\.(\d{4}\.\d{4,5})", re.I)


def _arxiv_id(ids):
    """从 OpenAlex ids/doi 里抠 arXiv 号:DOI 形如 10.48550/arxiv.2606.03834。"""
    for v in (ids or {}).values():
        m = ARXIV_DOI.search(str(v))
        if m:
            return m.group(1)
    return ""


def _abstract(inv):
    """abstract_inverted_index({word:[pos,...]}) 还原成正常文本。"""
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def _get(url, retries=3):
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "robot-intel/1.0 (https://github.com/robot-intel; mailto:robot-intel)"})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise last


def _to_record(w):
    aid = _arxiv_id(w.get("ids", {}))
    if not aid:
        return None
    loc = w.get("primary_location") or {}
    pub = w.get("publication_date") or ""
    authors = [(a.get("author") or {}).get("display_name", "")
               for a in (w.get("authorships") or [])]
    return {
        "arxiv_id": aid,
        "title": " ".join((w.get("title") or "").split()),
        "abstract": " ".join(_abstract(w.get("abstract_inverted_index")).split()),
        "authors": [a for a in authors if a],
        "categories": [],  # OpenAlex 无 arXiv 原始分类;留空(下游靠 title+keywords 过滤)
        "published": pub,
        "updated": pub,
        "url": f"https://arxiv.org/abs/{aid}",
        "pdf_url": loc.get("pdf_url") or f"https://arxiv.org/pdf/{aid}",
        "cited_by_count": w.get("cited_by_count", 0),
    }


def fetch_recent(terms, source_id, since_date, mailto,
                 per_page=200, terms_per_query=12, max_pages=2):
    """锁 arXiv 源 + 标题摘要 OR 多词,拉 since_date 起的最新论文,按 arxiv_id 去重。
       terms 分批(每批 terms_per_query 个 OR)避免 query 过长;每批翻最多 max_pages 页。"""
    by_id = {}
    batches = [terms[i:i + terms_per_query] for i in range(0, len(terms), terms_per_query)] or [[]]
    for batch in batches:
        # 注:arXiv 论文在 OpenAlex 里 type=preprint,别加 type:article(会全过滤掉);
        #     锁定到 arXiv 源本身已足够保证是 arXiv 预印本。
        filt = [f"primary_location.source.id:{source_id}",
                f"from_publication_date:{since_date}"]
        if batch:
            filt.append("title_and_abstract.search:" + "|".join(batch))
        cursor = "*"
        for _ in range(max_pages):
            params = {"filter": ",".join(filt), "per-page": str(per_page),
                      "sort": "publication_date:desc", "cursor": cursor}
            if mailto:
                params["mailto"] = mailto
            url = API + "?" + urllib.parse.urlencode(params)
            try:
                d = _get(url)
            except Exception as e:
                print(f"  OpenAlex 批次失败(跳过): {e}")
                break
            for w in d.get("results", []):
                rec = _to_record(w)
                if rec and rec["arxiv_id"] not in by_id:
                    by_id[rec["arxiv_id"]] = rec
            cursor = (d.get("meta") or {}).get("next_cursor")
            if not cursor or len(d.get("results", [])) < per_page:
                break
        time.sleep(0.5)  # 礼貌
    return list(by_id.values())
