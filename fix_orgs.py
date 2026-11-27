#!/usr/bin/env python3
"""机构核实回填:旧版只读摘要时,提示词让模型"依据作者名判断机构",结果大量乱猜
(看到中文名就写智元)。本脚本对近 N 天还没核实过机构的 arXiv 论文,下载 PDF,
只把**首页文字**给模型,让它照抄署名单位;首页没有就写 unknown。

幂等:analysis._org_src == "pdf" 的跳过。  用法: python fix_orgs.py [--days 30]
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

os.environ.setdefault("FULLTEXT_CACHE", str(Path(__file__).resolve().parent / ".cache" / "fulltext"))

from pipeline import analyze, config, export, fulltext, rank, store

PROMPT = """下面是一篇论文 PDF 首页的文字(标题、作者、单位、脚注、摘要开头,可能有排版噪声)。
请照着文字里写的作者单位填,只输出 JSON:
{{"org":"第一作者/通讯作者所在的主要机构,中文简称(如 北京大学、斯坦福、英伟达、智元机器人);文字里找不到任何单位、邮箱域名或机构名就写 unknown",
"orgs":["文字里出现的全部机构,中文简称,最多 6 个"],
"country":"主要机构所在地,从 [US, CN, JP, EU, UK, KR, Other, unknown] 选",
"org_type":"从 [company, university, institute, mixed, unknown] 选"}}
严禁根据作者姓名猜单位。只认文字里明写的。

首页文字:
{text}"""


def _arg(flag, default):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def main():
    cfg = config.load_config()
    days = int(_arg("--days", 30))
    llm = cfg["llm"]
    client = rank._client(llm)
    state = store.load()
    cut = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    day = lambda p: (p.get("first_seen") or p.get("published") or "")[:10]
    todo = [p for p in state["papers"]
            if day(p) >= cut and p.get("analysis") and p["analysis"].get("_org_src") != "pdf"
            and fulltext.ARXIV_RE.match(str(p.get("arxiv_id", "")))]
    todo.sort(key=rank.combo, reverse=True)
    print(f"待核实机构:近 {days} 天 {len(todo)} 篇", flush=True)
    if client is None or not todo:
        return
    with ThreadPoolExecutor(max_workers=3) as ex:          # 下载对 arXiv 客气点
        texts = list(ex.map(lambda p: fulltext.fetch(p["arxiv_id"], 3500), todo))
    print(f"  取到首页 {sum(1 for t in texts if t)}/{len(todo)}", flush=True)

    def one(pt):
        p, t = pt
        if not t:
            return 0
        try:
            r = client.chat.completions.create(
                model=llm.get("model", "qwen-plus"), max_tokens=300, temperature=0,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": PROMPT.format(text=t[:3500])}])
            d = analyze._parse_json(r.choices[0].message.content)
        except Exception:
            return 0
        a = p["analysis"]
        a["_org_guess"] = a.get("org", "")                 # 留底,便于回看当初猜成了什么
        orgs = [o for o in (d.get("orgs") or []) if o]
        a["org"] = "/".join(dict.fromkeys([d.get("org") or "unknown"] + orgs[:5])) if d.get("org") not in (None, "", "unknown") else "unknown"
        a["country"], a["org_type"] = d.get("country", "unknown"), d.get("org_type", "unknown")
        a["_org_src"] = "pdf"
        return 1
    with ThreadPoolExecutor(max_workers=8) as ex:
        ok = sum(ex.map(one, zip(todo, texts)))
    changed = sum(1 for p in todo if p["analysis"].get("_org_src") == "pdf"
                  and p["analysis"].get("_org_guess", "") != p["analysis"].get("org", ""))
    print(f"  核实 {ok} 篇,其中 {changed} 篇和原来猜的不一样")
    store.save(state)
    export.export(state, config.enabled_routes(cfg), datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))


if __name__ == "__main__":
    main()
