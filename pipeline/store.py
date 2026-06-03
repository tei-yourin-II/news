"""持久化状态。Day-1 用 JSON 当真相源(committed 进仓库 = GH Action 跨次运行的状态)。
Day-N 升级到 SQLite/Postgres 时,只换这一个文件即可。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORE = ROOT / "data" / "papers.json"


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


def upsert(state, records):
    """幂等:按 arxiv_id 去重合并。"""
    by_id = {p["arxiv_id"]: p for p in state.get("papers", [])}
    for r in records:
        by_id[r["arxiv_id"]] = r
    state["papers"] = sorted(
        by_id.values(), key=lambda p: p.get("scores", {}).get("total", 0), reverse=True)
    return state
