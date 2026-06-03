#!/usr/bin/env python3
"""生成 docs/llm_base.json:大厂 LLM 基模横向格局(各厂旗舰 + 实力分)。
从 baseline/llm_base_models.md 用 LLM 结构化。可重复跑。
(注:dynamics.json 里也有 domain=llm 的厂商卡;此文件是 dashboard 右栏/基模域用。)
"""
import json
import os

from pipeline import config

config.load_config()
from openai import OpenAI  # noqa: E402

client = OpenAI(api_key=os.environ["QWEN_API_KEY"],
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
SYS = ('把这份大厂基模调研结构化,输出JSON:\n'
       '{"vendors":[{"name":"厂商中文名","country":"US|CN|EU","flagship":"最新旗舰模型名",'
       '"score":实力分0-100整数,"note":"一句话定位"}],"verdict":"一句话总横评:谁更屌、中美格局"}\n'
       '覆盖所有厂商,按实力分排。只输出JSON。')


def main():
    md = open("baseline/llm_base_models.md", encoding="utf-8").read()[:24000]
    r = client.chat.completions.create(
        model="qwen-plus", max_tokens=4000, temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": SYS}, {"role": "user", "content": md}])
    d = json.loads(r.choices[0].message.content)
    d["generated_at"] = "2026-06-03"
    json.dump(d, open("docs/llm_base.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"llm_base.json: {len(d.get('vendors', []))} 厂商")


if __name__ == "__main__":
    main()
