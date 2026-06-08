"""持久化状态。Day-1 用 JSON 当真相源(committed 进仓库 = GH Action 跨次运行的状态)。
Day-N 升级到 SQLite/Postgres 时,只换这一个文件即可。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORE = ROOT / "data" / "papers.json"

_REAL_ID = re.compile(r"^\d{4}\.\d{4,5}$")        # 真实 arXiv 号(区别于 cs-* / 占位)
_NORM = re.compile(r"[^a-z0-9]+")


def norm_title(t):
    """标题归一(去标点/大小写/空白)做近重判定。"""
    return _NORM.sub("", (t or "").lower())


def load():
    if STORE.exists():
        with open(STORE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"papers": []}


def seen_ids(state):
    return {p["arxiv_id"] for p in state.get("papers", [])}


def save(state):
    STORE.parent.mkdir(parents=True, exist_ok=True)
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _better(a, b):
    """两条同一论文(标题归一相同)的记录,选保留哪条:
    真实 arXiv 号 > 占位(cs-*);其次总分高;再次有 analysis 的。"""
    a_real = bool(_REAL_ID.match(a["arxiv_id"]))
    b_real = bool(_REAL_ID.match(b["arxiv_id"]))
    if a_real != b_real:
        return a if a_real else b
    a_sc = a.get("scores", {}).get("total", 0) or 0
    b_sc = b.get("scores", {}).get("total", 0) or 0
    if a_sc != b_sc:
        return a if a_sc > b_sc else b
    return a if a.get("analysis") else b


def _merge(keep, drop):
    """保留 keep,把 drop 上 keep 缺的有用字段补过来(venue / source / first_seen 不丢)。"""
    if not keep.get("venue") and drop.get("venue"):
        keep["venue"] = drop["venue"]
    # 基石身份是有意的标注,合并时别弄丢
    if drop.get("source") == "cornerstone" and keep.get("source") != "cornerstone":
        keep.setdefault("also_cornerstone", True)
    ks, ds = keep.get("first_seen", ""), drop.get("first_seen", "")
    if ds and (not ks or ds < ks):     # first_seen 取更早的(时效基准更准)
        keep["first_seen"] = ds
    return keep


def dedup(papers):
    """跨记录去重:先按 arxiv_id 精确去重,再按标题归一并近重(占位↔真实撞车等),
    每组保留最优一条。返回去重后的列表 + 合并条数。"""
    by_id = {}
    for p in papers:           # 1) arxiv_id 精确(后来者覆盖,等价原 upsert)
        by_id[p["arxiv_id"]] = p
    by_title = {}              # 2) 标题归一并组
    for p in by_id.values():
        key = norm_title(p.get("title"))
        if not key:
            by_title[id(p)] = p   # 无标题不参与并组,各自保留
            continue
        if key in by_title:
            keep, drop = (p, by_title[key]) if _better(p, by_title[key]) is p else (by_title[key], p)
            by_title[key] = _merge(keep, drop)
        else:
            by_title[key] = p
    merged = len(by_id) - len(by_title)
    return list(by_title.values()), merged


def upsert(state, records):
    """幂等:按 arxiv_id 去重合并,并消解占位↔真实等近重(同标题只留最优一条)。"""
    papers, merged = dedup(list(state.get("papers", [])) + list(records))
    if merged:
        print(f"  [store] 去重合并 {merged} 篇近重(占位↔真实/同名)")
    state["papers"] = sorted(
        papers, key=lambda p: p.get("scores", {}).get("total", 0), reverse=True)
    return state
