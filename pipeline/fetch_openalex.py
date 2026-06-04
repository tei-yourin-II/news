#!/usr/bin/env python3
"""OpenAlex 取数:锁定预印本源(arXiv / bioRxiv)做关键词×日期检索。
arXiv 老 API(export.arxiv.org/api/query)从云 IP 几乎必 429;OpenAlex 是为轮询而生的开放目录,
带 mailto 进礼貌池后实测无 429,且白送 abstract / 被引用数 / venue / 机构。

- arXiv 源(S4306400194):key=arXiv 号(2606.03834),配 fetch_thumbs 抓图。
- bioRxiv 源(S4306402567):补脑机/蛋白冷门域(顶尖工作 arXiv 覆盖不到),key=DOI。
输出 schema 与 fetch_arxiv._parse 对齐,多带 cited_by_count + doi(供 fetch_quality_batch 复用,替掉 S2)。
零额外依赖(urllib + json)。
"""
import json
import re
import time
import urllib.parse
import urllib.request

API = "https://api.openalex.org/works"
ARXIV_DOI = re.compile(r"arxiv\.(\d{4}\.\d{4,5})", re.I)


def _ua():
    return {"User-Agent": "robot-intel/1.0 (https://github.com/tei-yourin-II/news; mailto:robot-intel)"}


def _clean_doi(w):
    """w['doi'] 形如 https://doi.org/10.48550/arxiv.xxx → 10.48550/arxiv.xxx。"""
    d = (w.get("doi") or "").strip()
    return d.replace("https://doi.org/", "").replace("http://doi.org/", "")


def _arxiv_id(ids, doi):
    """从 OpenAlex ids/doi 抠 arXiv 号。"""
    m = ARXIV_DOI.search(doi)
    if m:
        return m.group(1)
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
            req = urllib.request.Request(url, headers=_ua())
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise last


def _to_record(w, kind):
    doi = _clean_doi(w)
    if kind == "arxiv":
        key = _arxiv_id(w.get("ids", {}), doi)
        if not key:
            return None
        url = f"https://arxiv.org/abs/{key}"
        pdf = (w.get("primary_location") or {}).get("pdf_url") or f"https://arxiv.org/pdf/{key}"
    else:  # biorxiv / 其它预印本:用 DOI 当 key(fetch_thumbs 的 arXiv 正则不匹配 → 自动跳过抓图)
        if not doi:
            return None
        key = doi
        url = f"https://doi.org/{doi}"
        pdf = (w.get("primary_location") or {}).get("pdf_url") or url
    pub = w.get("publication_date") or ""
    authors = [(a.get("author") or {}).get("display_name", "")
               for a in (w.get("authorships") or [])]
    return {
        "arxiv_id": key,                        # 全管线统一主键(arXiv 号 / bioRxiv DOI)
        "doi": doi,                             # 供 fetch_quality_batch 复用
        "source_kind": kind,
        "title": " ".join((w.get("title") or "").split()),
        "abstract": " ".join(_abstract(w.get("abstract_inverted_index")).split()),
        "authors": [a for a in authors if a],
        "categories": [],
        "published": pub,
        "updated": pub,
        "url": url,
        "pdf_url": pdf,
        "cited_by_count": w.get("cited_by_count", 0),
    }


def fetch_recent(terms, source_id, since_date, mailto,
                 per_page=200, terms_per_query=12, max_pages=2, kind="arxiv"):
    """锁定 source_id + 标题摘要 OR 多词,拉 since_date 起的最新论文,按 key 去重。
       注:arXiv 论文在 OpenAlex 是 type=preprint,别加 type:article(会全过滤掉)。"""
    by_id = {}
    batches = [terms[i:i + terms_per_query] for i in range(0, len(terms), terms_per_query)] or [[]]
    for batch in batches:
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
                rec = _to_record(w, kind)
                if rec and rec["arxiv_id"] not in by_id:
                    by_id[rec["arxiv_id"]] = rec
            cursor = (d.get("meta") or {}).get("next_cursor")
            if not cursor or len(d.get("results", [])) < per_page:
                break
        time.sleep(0.5)  # 礼貌
    return list(by_id.values())


def fetch_quality_batch(dois, mailto, chunk=50):
    """按 DOI 批量取 cited_by_count + venue —— 替掉逐篇限流的 Semantic Scholar。
       入参 dois: ['10.48550/arxiv.xxx', '10.1101/yyy', ...](即 record['doi'])。
       返回 {doi: {'citations', 'influential_citations', 'venue'}}。"""
    out = {}
    dois = [d for d in dict.fromkeys(dois) if d]
    for i in range(0, len(dois), chunk):
        batch = dois[i:i + chunk]
        filt = "doi:" + "|".join(batch)
        params = {"filter": filt, "per-page": str(chunk), "mailto": mailto}
        url = API + "?" + urllib.parse.urlencode(params)
        try:
            d = _get(url)
        except Exception as e:
            print(f"  OpenAlex 引用批量失败(跳过): {e}")
            continue
        for w in d.get("results", []):
            doi = _clean_doi(w)
            venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
            out[doi] = {
                "citations": w.get("cited_by_count", 0),
                "influential_citations": 0,   # OpenAlex 无此字段;quality_score 里权重小,置 0 不影响排序
                "venue": venue,
            }
        time.sleep(0.3)
    return out
