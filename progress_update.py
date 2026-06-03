#!/usr/bin/env python3
"""领域进展门控更新:领域进展(progress.json 的基石榜)是**慢变量**,只在真突破时才动。
逻辑:每日新论文里,凡 significance ≥ 阈值(对标基石够高)的,交 LLM 判断
"够不够格进该领域基石榜/是否改写横评";够 → 纳入 works + 记 changelog;不够 → 原封不动。
没大突破的日子,这脚本啥也不改 —— 这正是设计意图。
跑在 daily.py 里(run.py 之后)。
"""
import json
import os
from pathlib import Path

from pipeline import config, store

ROOT = Path(__file__).resolve().parent
PROG = ROOT / "docs" / "progress.json"
LOG = ROOT / "docs" / "progress_changelog.json"
GATE = 80          # 分量分门槛:低于此连考虑都不考虑(慢变量,门要高)

config.load_config()
from openai import OpenAI  # noqa: E402

client = OpenAI(api_key=os.environ.get("QWEN_API_KEY", ""),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

# route → progress topic
R2T = {"vla": "vla", "world_model": "world_model", "whole_body_control": "whole_body_control",
       "dexterous_manipulation": "dexterous_manipulation", "sim2real_data": "sim2real_data",
       "hardware_unitree": "hardware_unitree", "bci_neural_decoding": "bci",
       "bci_foundation_models": "bci", "bci_embodied_robot": "bci", "bci_noninvasive_eeg": "bci",
       "protein_ai": "ai_science", "genomics_ai": "ai_science",
       "protein_structure_design": "ai_science", "genomic_foundation_model": "ai_science"}


def _judge(topic, paper):
    a = paper.get("analysis", {})
    top = "; ".join(f"{w['name']}={w.get('significance')}" for w in topic.get("works", [])[:10])
    prompt = f"""领域「{topic['name']}」当前基石榜(分量分):{top}
当前横评:{topic.get('verdict', '')}

新论文:《{paper['title']}》 分量{a.get('significance')}
摘要:{a.get('tldr', '')}

这篇够不够格进该领域**基石榜**(即:是否范式级/明显改变格局,而非普通推进)?挑剔点。
只输出JSON: {{"promote":true/false,"significance":修正后分量0-100,"why":"中文一句","new_verdict":"若需改写横评则给新的,否则空字符串"}}"""
    try:
        r = client.chat.completions.create(
            model="qwen-plus", max_tokens=300, temperature=0,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}])
        t = r.choices[0].message.content
        return json.loads(t[t.find("{"):t.rfind("}") + 1])
    except Exception as e:
        print(f"  判定失败,跳过: {e}")
        return {"promote": False}


def main():
    if not PROG.exists():
        print("无 progress.json,跳过")
        return
    prog = json.loads(PROG.read_text(encoding="utf-8"))
    topics = prog.get("topics", {})
    papers = store.load()["papers"]
    log = json.loads(LOG.read_text(encoding="utf-8")) if LOG.exists() else {"changes": []}

    # 候选:非基石(每日新论文)、分量≥门槛、且其标题还不在基石榜里
    changed = 0
    for p in papers:
        if p.get("source") == "cornerstone":
            continue
        a = p.get("analysis", {})
        if (a.get("significance", 0) or 0) < GATE:
            continue
        tid = R2T.get(p.get("best_route"))
        topic = topics.get(tid)
        if not topic:
            continue
        if any(w.get("name", "").lower() == p["title"].lower() for w in topic.get("works", [])):
            continue
        v = _judge(topic, p)
        if not v.get("promote"):
            print(f"  ✗ 未达基石: {p['title'][:48]} (分量{a.get('significance')})")
            continue
        # 纳入基石榜
        topic.setdefault("works", []).insert(0, {
            "name": p["title"], "org": a.get("org", ""), "country": a.get("country", ""),
            "year": (p.get("published", "") or "")[:4], "arxiv_id": p["arxiv_id"],
            "significance": v.get("significance", a.get("significance")), "why": v.get("why", "")})
        topic["works"] = sorted(topic["works"], key=lambda w: -(w.get("significance") or 0))
        if v.get("new_verdict"):
            topic["verdict"] = v["new_verdict"]
        log["changes"].append({"topic": tid, "paper": p["title"], "arxiv_id": p["arxiv_id"],
                               "significance": v.get("significance"), "why": v.get("why")})
        changed += 1
        print(f"  ★ 晋升基石: {p['title'][:48]} → {topic['name']}")

    if changed:
        PROG.write_text(json.dumps(prog, ensure_ascii=False, indent=2), encoding="utf-8")
        LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"领域进展更新:晋升 {changed} 篇(无突破则为0=领域进展不变,符合预期)")


if __name__ == "__main__":
    main()
