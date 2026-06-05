"""LLM 成分分析:对一篇论文做结构化拆解 + 主观打分(新颖/证据/可复现)。
支持三类后端,任一不可用都优雅降级出占位(不阻断主流程):
  - provider=qwen / openai → 走 OpenAI 兼容端点(DashScope 等),需 QWEN_API_KEY/OPENAI_API_KEY
  - provider=anthropic       → 走 Claude,需 ANTHROPIC_API_KEY
  - provider=none / 缺 key/缺库 → 占位
"""
import json
import os

SYSTEM = """你是科技情报系统的资深论文分析员,覆盖三大领域:具身智能/机器人、脑机接口、AI×科学/生物(蛋白质/基因组/药物/分子)。给定一篇论文的标题和摘要,做"成分分析"——不要写"提出新方法很有前景"这种废话,要拆解到可判断。对 AI×科学/生物 类论文,robot_dependency/sim2real_status 等机器人专属字段填 none/n/a 即可,重点看科学问题的实证质量。

⚠️ 面向人阅读的字段(tldr / claim / input / output / one_sentence_verdict)**必须用简体中文**,即使论文是英文;枚举/标签类字段(method_components / sim2real_status / generalization / reproducibility / tags)保持给定的英文取值。

只输出一个 JSON 对象,字段如下:
{
  "tldr": "用一句中文白话讲清这篇到底做了啥、解决什么问题(给完全没读过的人看)",
  "org": "主要团队/机构(中文简称,如 英伟达/谷歌DeepMind/Meta/斯坦福/伯克利/清华/智元/宇树/银河通用;依据作者名与摘要里的署名判断,多个取最主要的一个;实在判断不了写 unknown)",
  "country": "该机构所属国家/地区,从 [US, CN, JP, EU, UK, KR, Other, unknown] 里选一个(美国US/中国CN/日本JP/欧洲EU/英国UK/韩国KR)",
  "org_type": "发布机构类型,从 [company, university, institute, mixed, unknown] 选一个(企业/高校/研究机构/产学研合作/未知)",
  "claim": "论文最核心的一句话主张(中文)",
  "method_components": ["model","dataset","simulator","policy","benchmark","hardware","ui" 里命中的],
  "input": "输入是什么(中文,如 RGB图像+语言指令)",
  "output": "输出是什么(中文,如 动作块/轨迹)",
  "robot_dependency": "依赖的机器人/仿真器/传感器(中文),没有写 none",
  "data_dependency": "对真实机器人数据的依赖程度(中文)",
  "sim2real_status": "sim-only | small-real | multi-embodiment | deployed | n/a",
  "generalization": "跨任务/跨场景/跨机体/跨用户 中命中的,或 limited",
  "reproducibility": "code+model+data | code-only | project-page | none | unknown",
  "tags": ["从 multimodal-fusion,tactile,dexterous,sim2real,teleoperation,dataset,benchmark,open-source,real-robot,large-scale 里命中的"],
  "novelty": 0,            // 0-10 真突破=10 概念包装=2
  "evidence": 0,           // 0-12 真机多任务多baseline有消融=12 纯概念=2
  "reproducibility_score": 0,  // 0-8 全开源=8 啥都没=0
  "significance": 0,       // 0-100 分量分:这篇对领域的真实价值,要挑剔!⚠️忽略作者自吹的"突破性/novel/SOTA/first/state-of-the-art"等措辞(人人都写),只看实质证据。标尺:90-100=里程碑(开新范式/解决长期开放难题,如AlphaFold/RT-2级);75-89=重磅(明显推进SOTA且证据扎实:真机+多任务+消融+开源);60-74=显著贡献;40-59=扎实增量;20-39=一般/窄/纯benchmark;0-19=灌水/纯概念包装。自吹但无实证、只仿真小数据、纯刷榜的一律压到40以下。
  "significance_reason": "给这个分量分的一句话中文理由(点明它是真推进还是包装)",
  "one_sentence_verdict": "一句话判断(中文),从 真突破/工程整合/概念包装/暂时不用看 里选一个并简述为什么"
}
严格只输出 JSON,不要 markdown 代码块。"""


def _stub(paper):
    return {
        "tldr": paper["title"],
        "org": "unknown",
        "country": "unknown",
        "org_type": "unknown",
        "claim": paper["title"],
        "method_components": [], "input": "", "output": "",
        "robot_dependency": "unknown", "data_dependency": "unknown",
        "sim2real_status": "n/a", "generalization": "unknown",
        "reproducibility": "unknown", "tags": [],
        "novelty": 0, "evidence": 0, "reproducibility_score": 0,
        "significance": 0, "significance_reason": "",
        "one_sentence_verdict": "[未配置 LLM,占位] " + paper["title"][:80],
        "_llm": "stub",
    }


def _parse_json(text):
    """容错解析 LLM 返回的 JSON(剥 markdown 代码块)。"""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`").split("\n", 1)[-1].rsplit("```", 1)[0]
    return json.loads(text)


def _user_content(paper):
    """喂给 LLM 的内容:标题 + 作者(供推断机构)+ 摘要 + 该领域基石参照(校准分量分)。"""
    authors = ", ".join(paper.get("authors", [])[:12])
    base = (f"标题: {paper['title']}\n\n"
            f"作者: {authors or '(未提供)'}\n\n"
            f"摘要: {paper['abstract']}")
    anchors = paper.get("_anchors")
    if anchors:
        base += (f"\n\n【该领域基石参照(分量分标尺,衡量本文水平用)】:\n{anchors}\n"
                 "请据此给本文的 significance 定位:明显不如这些基石就给低分,"
                 "达到或超越某档才给对应高分。别被作者自吹影响。")
    return base


# 各 provider 的环境变量约定与默认端点
_OPENAI_COMPAT = {
    "qwen": {
        "key_envs": ["QWEN_API_KEY", "DASHSCOPE_API_KEY", "OPENAI_API_KEY"],
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    },
    "openai": {"key_envs": ["OPENAI_API_KEY"], "base_url": None},
}


def _resolve_key(env_names):
    for name in env_names:
        v = os.environ.get(name)
        if v:
            return v
    return None


def _analyze_openai_compat(paper, llm_cfg, provider):
    """OpenAI 兼容端点(Qwen via DashScope / OpenAI 等)。"""
    try:
        from openai import OpenAI
    except ImportError:
        return _stub(paper)
    spec = _OPENAI_COMPAT[provider]
    key = _resolve_key(spec["key_envs"])
    if not key:
        return _stub(paper)
    base_url = llm_cfg.get("base_url") or spec["base_url"]
    try:
        client = OpenAI(api_key=key, base_url=base_url)
        resp = client.chat.completions.create(
            model=llm_cfg.get("model", "qwen-plus"),
            max_tokens=1024,
            temperature=0.2,
            response_format={"type": "json_object"},  # 强制 JSON,省去剥壳
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": _user_content(paper)},
            ],
        )
        data = _parse_json(resp.choices[0].message.content)
        data["_llm"] = llm_cfg.get("model")
        return data
    except Exception as e:
        print(f"  [analyze] {provider} 失败,出占位: {e}")
        return _stub(paper)


def _analyze_anthropic(paper, llm_cfg):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return _stub(paper)
    try:
        import anthropic
    except ImportError:
        return _stub(paper)
    try:
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=llm_cfg.get("model", "claude-sonnet-4-6"),
            max_tokens=1024,
            system=[{"type": "text", "text": SYSTEM,
                     "cache_control": {"type": "ephemeral"}}],  # 静态 system 走缓存省钱
            messages=[{"role": "user", "content": _user_content(paper)}],
        )
        data = _parse_json(msg.content[0].text)
        data["_llm"] = llm_cfg.get("model")
        return data
    except Exception as e:
        print(f"  [analyze] anthropic 失败,出占位: {e}")
        return _stub(paper)


def analyze(paper, llm_cfg):
    provider = llm_cfg.get("provider", "none")
    if provider in _OPENAI_COMPAT:
        return _analyze_openai_compat(paper, llm_cfg, provider)
    if provider == "anthropic":
        return _analyze_anthropic(paper, llm_cfg)
    return _stub(paper)
