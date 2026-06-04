#!/usr/bin/env python3
"""生成 docs/progress.json:各领域**基石标尺**(works,带 significance)+ 代表玩家 + 横评。
基石=衡量新论文水平的锚点;新论文 significance 对标这些(见 run.py._load_anchors)。
从各 baseline 用 LLM 抽取。可重复跑(基线更新/新突破时重跑)。
跑完通常接着跑 ingest_cornerstones.py 把基石灌进论文库。
"""
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from pipeline import config

config.load_config()
from openai import OpenAI  # noqa: E402

client = OpenAI(api_key=os.environ["QWEN_API_KEY"],
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

TOPICS = [
    ("vla", "VLA 视觉-语言-动作", "embodied_ai"),
    ("world_model", "世界模型 / WAM", "embodied_ai"),
    ("whole_body_control", "全身控制 / 人形", "embodied_ai"),
    ("dexterous_manipulation", "灵巧操作", "embodied_ai"),
    ("sim2real_data", "Sim2Real / 数据", "embodied_ai"),
    ("hardware_unitree", "硬件 / 人形整机", "embodied_ai"),
    ("bci", "脑机接口", "bci"),
    ("ai_science", "AI×科学 / 生物", "ai_science"),
]
SYS = ('你是领域情报分析员。下面是某领域的深度调研基线。抽取该领域的**基石/里程碑工作**'
       '(cornerstones——绕不开的奠基与重磅,作为衡量后续新论文水平的标尺锚点)。输出 JSON:\n'
       '{"works":[{"name":"工作/模型名","org":"机构中文","country":"US|CN|JP|EU|UK",'
       '"year":"年份","arxiv_id":"有则填否则空","significance":分量0-100,"why":"一句话为何是基石"}],\n'
       '"players":[{"name":"机构中文简称","country":"US|CN|JP|EU|UK","type":"company|university|institute","note":"代表作"}],\n'
       '"verdict":"一句话挑剔横评:中美各家谁更领先谁追赶","activity":"该领域当前活跃度一句话"}\n'
       '⚠️significance标尺:真正开宗立派/范式级=92-99,重磅推进=80-91,重要但非颠覆=72-79。'
       'works取15-22篇按significance降序,务必含领域内公认重磅。players≤10。中文。只输出JSON。')


def gen(args):
    tid, name, dom = args
    md = open(f"baseline/{tid}.md", encoding="utf-8").read()[:24000]
    r = client.chat.completions.create(
        model="qwen-plus", max_tokens=6000, temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": SYS},
                  {"role": "user", "content": f"领域:{name}\n\n{md}"}])
    d = json.loads(r.choices[0].message.content)
    d.update({"id": tid, "name": name, "domain": dom, "last_updated": "2026-06-03"})
    d["works"] = sorted(d.get("works", []), key=lambda w: -(w.get("significance") or 0))
    print(f"  {name}: {len(d['works'])} 基石")
    return tid, d


def main():
    with ThreadPoolExecutor(max_workers=4) as ex:
        out = dict(ex.map(gen, TOPICS))
    json.dump({"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "topics": out},
              open("docs/progress.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"progress.json: {len(out)} 领域")


if __name__ == "__main__":
    main()
