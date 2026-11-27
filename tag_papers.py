#!/usr/bin/env python3
"""给存量论文补方法标签(pipeline/approach.py 的词表)。新论文在 run.py 拆解时就会带上。
幂等:已有 approach 字段的跳过(--force 重打)。  用法: python tag_papers.py [--days 30] [--force]
"""
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from pipeline import analyze, approach, config, export, rank, store


def _arg(flag, default):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def main():
    cfg = config.load_config()
    days, force = int(_arg("--days", 30)), "--force" in sys.argv
    llm = cfg["llm"]
    client = rank._client(llm)
    state = store.load()
    cut = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    day = lambda p: (p.get("first_seen") or p.get("published") or "")[:10]
    todo = [p for p in state["papers"] if p.get("analysis") and day(p) >= cut
            and (force or "approach" not in p["analysis"])]
    print(f"待打标签:近 {days} 天 {len(todo)} 篇", flush=True)
    if client is None or not todo:
        return

    def one(p):
        a = p["analysis"]
        text = (p.get("abstract") or "")[:2500] or f"{a.get('tldr', '')} {a.get('claim', '')}"
        for attempt in range(4):
            try:
                r = client.chat.completions.create(
                    model=llm.get("model", "qwen-plus"), max_tokens=120, temperature=0,
                    response_format={"type": "json_object"},
                    messages=[{"role": "user", "content": approach.PROMPT.format(
                        menu=approach.menu(), title=p["title"], text=text)}])
                a["approach"] = approach.clean(analyze._parse_json(r.choices[0].message.content).get("approach"))
                return 1
            except Exception as e:
                if "429" in str(e):
                    time.sleep(5 * (attempt + 1))      # 限流就退避重试,别整批放弃
                    continue
                return 0
        return 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        ok = sum(ex.map(one, todo))
    c = Counter(t for p in todo for t in p["analysis"].get("approach", []))
    print(f"  成功 {ok}/{len(todo)};没打上任何标签的 {sum(1 for p in todo if not p['analysis'].get('approach'))} 篇")
    print("  " + " ".join(f"{k}:{v}" for k, v in c.most_common()))
    store.save(state)
    export.export(state, config.enabled_routes(cfg), datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))


if __name__ == "__main__":
    main()
