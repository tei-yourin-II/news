"""相关度过滤。
后端二选一(自动降级):
  1. sentence-transformers(若已安装)—— 语义嵌入,质量高
  2. 关键词重叠(纯标准库)—— 零依赖兜底,Day-1 默认可用
兴趣画像 = 每条路线的 (name + keywords + seed 标题) 文本。
"""
import math
import re

_WORD = re.compile(r"[a-z0-9\-]+")


def _tokens(text):
    return set(_WORD.findall((text or "").lower()))


def build_profiles(routes):
    """每条路线一个文本画像 + 权重。"""
    profiles = []
    for r in routes:
        seed_titles = " ".join(s.get("title", "") for s in r.get("seeds", []))
        kws = " ".join(r.get("keywords", []))
        text = f"{r['name']} {kws} {seed_titles}"
        profiles.append({
            "id": r["id"], "name": r["name"], "weight": r.get("weight", 1.0),
            "text": text, "tokens": _tokens(text),
            "keywords": [k.lower() for k in r.get("keywords", [])],
        })
    return profiles


# ---------- 嵌入后端(可选) ----------
def _get_embedder():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


# ---------- 关键词后端(兜底) ----------
def _keyword_score(paper_tokens, paper_text_low, profile):
    """关键词命中是必要条件:没命中任何路线关键词的论文(纯靠通用词重叠)
    一律封顶,会被相关度阈值过滤 —— 避免把泛 AI 论文(MoE/RAG/LLM 等)误收。"""
    kw_hits = sum(1 for k in profile["keywords"] if k in paper_text_low)
    inter = paper_tokens & profile["tokens"]
    union = paper_tokens | profile["tokens"]
    jacc = len(inter) / len(union) if union else 0.0
    if kw_hits == 0:
        return min(jacc * 0.6, 0.10)          # 无关键词命中 → 封顶 0.10,基本被过滤
    return min(0.20 + kw_hits * 0.12 + jacc * 1.0, 1.0)  # 有命中 → 起步 0.32,稳过


def in_domain(text_low, anchor_terms):
    """领域硬门:标题+摘要里命中任一领域锚点词才算"沾边"。
    锚点用宽召回单词(robot/manipulation/humanoid/EEG/BCI…),挡掉纯 NLP/LLM 论文 ——
    嵌入相似度对任何 ML 文本都给中等分,光靠语义阈值挡不住,必须配关键词硬门。"""
    if not anchor_terms:
        return True
    return any(t in text_low for t in anchor_terms)


def score_papers(papers, profiles, anchor_terms=None):
    """给每篇打 {best_route, route_scores, relevance(0~1)}。原地添加字段并返回。
    anchor_terms: 领域锚点词(小写);命中不到的论文直接判域外(relevance 封顶 0.05)。"""
    embedder = _get_embedder()
    backend = "embedding" if embedder else "keyword"
    anchors = [t.lower() for t in (anchor_terms or [])]

    if embedder:
        prof_vecs = embedder.encode([p["text"] for p in profiles], normalize_embeddings=True)
        paper_vecs = embedder.encode(
            [f"{p['title']}. {p['abstract']}" for p in papers], normalize_embeddings=True)

    for i, p in enumerate(papers):
        plow = f"{p['title']} {p['abstract']}".lower()
        scores = {}
        if embedder:
            for j, prof in enumerate(profiles):
                sim = float(_cosine(paper_vecs[i], prof_vecs[j]))
                scores[prof["id"]] = max(0.0, (sim + 0.05)) * prof["weight"]
        else:
            ptoks = _tokens(plow)
            for prof in profiles:
                scores[prof["id"]] = _keyword_score(ptoks, plow, prof) * prof["weight"]
        best = max(scores, key=scores.get) if scores else None
        raw = round(scores.get(best, 0.0), 4) if best else 0.0
        # 领域硬门:不沾边的(纯 NLP/LLM 等)无论语义多高一律压到阈值下
        if not in_domain(plow, anchors):
            raw = min(raw, 0.05)
        p["route_scores"] = {k: round(v, 4) for k, v in scores.items()}
        p["best_route"] = best
        p["relevance_raw"] = raw
    return papers, backend
