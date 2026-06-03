"""可选:把论文 upsert 到 Notion 数据库。
需要环境变量 NOTION_TOKEN + NOTION_DB_ID,且 DB 有对应属性。
没配则静默跳过(不阻断管线)。Day-1 可先不配,只看 dashboard。
"""
import json
import os
import urllib.request

API = "https://api.notion.com/v1/pages"


def sync(records):
    token = os.environ.get("NOTION_TOKEN")
    db = os.environ.get("NOTION_DB_ID")
    if not token or not db:
        print("  [notion] 未配置 NOTION_TOKEN/NOTION_DB_ID,跳过")
        return 0
    ok = 0
    for p in records:
        try:
            _create_page(token, db, p)
            ok += 1
        except Exception as e:
            print(f"  [notion] {p['arxiv_id']} 写入失败: {e}")
    print(f"  [notion] 写入 {ok}/{len(records)} 篇")
    return ok


def _create_page(token, db, p):
    a = p.get("analysis", {})
    s = p.get("scores", {})
    props = {
        "Title": {"title": [{"text": {"content": p["title"][:1900]}}]},
        "arXiv": {"rich_text": [{"text": {"content": p["arxiv_id"]}}]},
        "Route": {"select": {"name": p.get("best_route") or "n/a"}},
        "Grade": {"select": {"name": p.get("grade") or "D"}},
        "Priority": {"select": {"name": p.get("read_priority") or "D"}},
        "Total": {"number": s.get("total", 0)},
        "Verdict": {"rich_text": [{"text": {"content": a.get("one_sentence_verdict", "")[:1900]}}]},
        "URL": {"url": p.get("url")},
    }
    body = json.dumps({"parent": {"database_id": db}, "properties": props}).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    })
    urllib.request.urlopen(req, timeout=30).read()
