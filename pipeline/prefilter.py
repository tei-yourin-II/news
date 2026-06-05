"""LLM 初筛:用廉价模型(qwen-turbo)批量判断论文是否属于本系统两大领域,并分路线。
放在「免费锚点门」之后、「贵的深拆解」之前 —— 三级漏斗的中间层。
标题+一句话就够判,批量 40 篇/次,token 极省。失败优雅降级(全部放行,不阻断)。
"""
import json
import os

from .analyze import _OPENAI_COMPAT, _resolve_key, _parse_json


# 领域人话描述(初筛员据此判断在不在范围内);键对齐 config 各路线的 domain 字段
_DOMAIN_DESC = {
    "embodied_ai": "具身智能:机器人/人形/VLA/操作抓取/运动控制/仿真与机器人数据/机器人硬件",
    "bci": "脑机接口:神经解码/脑机接口/神经假肢/EEG/神经基础模型/脑控机器人",
    "ai_science": "AI×科学/生物:蛋白质结构预测与设计(AlphaFold/ESM/RFdiffusion)、"
                  "基因组/DNA语言模型、单细胞、药物发现/分子生成、酶设计等用 AI 做科学的工作",
}


def _route_menu(routes):
    # 按 domain 分组列路线,让初筛员看清每个领域下有哪些细分
    by_dom = {}
    for r in routes:
        by_dom.setdefault(r.get("domain", "embodied_ai"), []).append(r)
    out = []
    for dom, rs in by_dom.items():
        out.append(f"  【{_DOMAIN_DESC.get(dom, dom).split(':')[0]}】")
        out += [f"    - {r['id']}: {r['name']}" for r in rs]
    return "\n".join(out)


def _prompt(routes, batch):
    doms = []
    for d in dict.fromkeys(r.get("domain", "embodied_ai") for r in routes):
        doms.append("- " + _DOMAIN_DESC.get(d, d))
    domain_block = "\n".join(doms)
    menu = _route_menu(routes)
    lines = "\n".join(f"{i}. {p['title']}" for i, p in enumerate(batch))
    return f"""你是一个科技情报系统的初筛员。本系统覆盖以下领域,判断每篇论文是否属于其中之一:
{domain_block}

⚠️ 与上述领域**都无关**的(如纯 NLP/纯文本任务/纯 CV/纯理论/推荐系统/多语言/水印/通用 agent 框架),relevant=false。
✅ 注意:AI 用于蛋白质/基因组/药物/分子等科学问题的论文**属于「AI×科学/生物」**,要保留,别因为"不是机器人"就拒。

可选路线 id(按领域分组):
{menu}
  - none: 不相关

论文列表:
{lines}

只输出 JSON: {{"results":[{{"i":0,"relevant":true,"route":"protein_ai"}}, ...]}}。每篇都要有一项,relevant=false 时 route 填 none。不要 markdown。"""


def classify(papers, routes, cfg, batch_size=40):
    """返回 {arxiv_id: {"relevant": bool, "route": str}}。出错/未配置则全部放行。"""
    provider = cfg.get("provider", "qwen")
    if provider not in _OPENAI_COMPAT:
        return {p["arxiv_id"]: {"relevant": True, "route": p.get("best_route")} for p in papers}
    key = _resolve_key(_OPENAI_COMPAT[provider]["key_envs"])
    if not key:
        return {p["arxiv_id"]: {"relevant": True, "route": p.get("best_route")} for p in papers}
    try:
        from openai import OpenAI
    except ImportError:
        return {p["arxiv_id"]: {"relevant": True, "route": p.get("best_route")} for p in papers}

    base_url = cfg.get("base_url") or _OPENAI_COMPAT[provider]["base_url"]
    client = OpenAI(api_key=key, base_url=base_url)
    model = cfg.get("model", "qwen-turbo")
    valid_routes = {r["id"] for r in routes}
    out = {}

    for k in range(0, len(papers), batch_size):
        batch = papers[k:k + batch_size]
        try:
            resp = client.chat.completions.create(
                model=model, max_tokens=2048, temperature=0,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": _prompt(routes, batch)}],
            )
            data = _parse_json(resp.choices[0].message.content)
            for item in data.get("results", []):
                idx = item.get("i")
                if idx is None or idx >= len(batch):
                    continue
                p = batch[idx]
                route = item.get("route")
                out[p["arxiv_id"]] = {
                    "relevant": bool(item.get("relevant")) and route in valid_routes,
                    "route": route if route in valid_routes else None,
                }
        except Exception as e:
            print(f"  [prefilter] 批次失败,本批放行: {e}")
            for p in batch:
                out.setdefault(p["arxiv_id"], {"relevant": True, "route": p.get("best_route")})
    # 兜底:没被判到的放行
    for p in papers:
        out.setdefault(p["arxiv_id"], {"relevant": True, "route": p.get("best_route")})
    return out
