#!/usr/bin/env python3
"""生成 docs/dynamics.json:以**企业为中心**的动态情报。
每家公司:综合实力 + 多维强项评估(轴按领域定) + 代表产品 + 近期动态。
从调研基线用 LLM 结构化;可重复跑(常用常更新),将来接 RSS 新闻后每日刷新。
"""
import json
import os
from concurrent.futures import ThreadPoolExecutor

from pipeline import config

config.load_config()
from openai import OpenAI  # noqa: E402

client = OpenAI(api_key=os.environ["QWEN_API_KEY"],
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

AXES = {
    "embodied": ["技术", "硬件", "量产", "数据", "资本", "生态"],
    "bci": ["技术", "临床落地", "硬件通道", "资本", "生态"],
    "llm": ["综合", "推理", "代码", "多模态", "开源", "性价比"],
}
# 领域 → 喂哪些基线文件
SRC = {
    "embodied": ["companies_cn_jp_us.md", "hardware_unitree.md"],
    "bci": ["companies_cn_jp_us.md", "bci.md"],
    "llm": ["llm_base_models.md"],
}
DOMAIN_CN = {"embodied": "具身智能/机器人", "bci": "脑机接口", "llm": "大厂LLM基模"}


def _prompt(domain):
    axes = "、".join(AXES[domain])
    return f"""下面是中/美/日「{DOMAIN_CN[domain]}」领域的调研基线。请以**企业为中心**为每家公司输出结构化情报评估。
只输出 JSON:
{{"companies":[{{
  "name":"公司中文名","country":"US|CN|JP|EU|UK",
  "overall":综合实力0-100整数,
  "positioning":"一句话定位",
  "strengths":{{ {", ".join(f'"{a}":0到100整数' for a in AXES[domain])} }},
  "products":["代表产品/型号(带关键参数,如 G1 ¥9.9万 / GPT-5.5)",...最多6个],
  "dynamics":["近期重大动态(带时间,如 2026-06 IPO过会)",...3到5条]
}}]}}
⚠️ 挑剔打分,有实证的高分、PR吹的低分。覆盖基线里所有公司。中文。strengths 的轴必须是:{axes}。只输出JSON,不要markdown。"""


def gen(domain):
    text = "\n\n".join(open(f"baseline/{f}", encoding="utf-8").read()
                       for f in SRC[domain] if os.path.exists(f"baseline/{f}"))[:30000]
    r = client.chat.completions.create(
        model="qwen-plus", max_tokens=8000, temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": _prompt(domain)},
                  {"role": "user", "content": text}])
    comps = json.loads(r.choices[0].message.content).get("companies", [])
    for c in comps:
        c["domain"] = domain
    print(f"  {domain}: {len(comps)} 家")
    return comps


def main():
    with ThreadPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(gen, ["embodied", "bci", "llm"]))
    companies = [c for r in results for c in r]
    out = {"generated_at": "2026-06-03", "axes": AXES, "companies": companies}
    json.dump(out, open("docs/dynamics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"dynamics.json: 共 {len(companies)} 家")


if __name__ == "__main__":
    main()
