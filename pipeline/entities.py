"""机构实体归一(entity resolution)——关系图最高杠杆的修复。

问题:LLM 把同一机构写成 NVIDIA / 英伟达 / NVIDIA GEAR Lab / "X & NVIDIA",
导致一个机构裂成十几个弱连接节点,产业枢纽消失;复合机构被当单节点,合作边被吞。

本模块:把一条 org 原始串 → 一组规范机构(canonical, 带国家)。
- 按分隔符拆开复合机构("CMU & Meta" → [CMU, Meta]),于是论文能连多条 by 边 = 真·合作边。
- 每个片段去噪声后缀后查 entities.yaml 的别名表(精确/子串/缩写词边界)归一。
- 噪声机构(未知/多机构/学术联合…)直接丢弃,不建节点。

零新依赖(只用 pyyaml,项目已依赖)。字典找不到的片段保留清理后的原名(country=unknown),
不丢信息,只是暂不合并——后续往 entities.yaml 补别名即可,加法式。
"""
import re
from functools import lru_cache
from pathlib import Path

import yaml

_YAML = Path(__file__).resolve().parent.parent / "entities.yaml"

# 复合机构分隔符:& / + 、 ， , and 和  (注意 "Google DeepMind" 内部空格不拆)
_SPLIT = re.compile(r"\s*(?:&|/|\+|、|，|,|；|;|\band\b|和)\s*")
# 片段末尾的噪声后缀(子团队/联合/等)
_SUFFIX = re.compile(
    r"(实验室|团队|课题组|联合团队|联合|联盟|等团队|等联合|等国际联盟|等|国际联盟)+$"
)
_PARENS = re.compile(r"[（(].*?[)）]")  # 去成对括号补充说明
_OPENP = re.compile(r"[（(].*$")         # 去未闭合括号(被分隔符拆断时)残留


@lru_cache(maxsize=1)
def _load():
    try:
        raw = yaml.safe_load(_YAML.read_text(encoding="utf-8")) or {}
    except Exception:
        raw = {}
    drop = {_norm(x) for x in raw.get("drop", [])}
    orgs = raw.get("orgs", {}) or {}
    # 构建别名 → (canonical, country) 索引;canonical 自身也是别名
    alias_idx = {}      # 规范化别名 -> canonical
    country = {}        # canonical -> country
    for canon, meta in orgs.items():
        meta = meta or {}
        country[canon] = meta.get("country", "unknown")
        names = [canon] + list(meta.get("aliases", []))
        for nm in names:
            alias_idx[_norm(nm)] = canon
    # 别名按长度降序,匹配时长名优先(避免 "Berkeley" 抢了 "UC Berkeley")
    ordered = sorted(alias_idx.items(), key=lambda kv: -len(kv[0]))
    return drop, alias_idx, ordered, country


def _norm(s):
    return re.sub(r"\s+", "", (s or "").strip().lower())


def _resolve_fragment(frag):
    """单个片段 → (canonical, country) 或 None(噪声/空)。"""
    drop, alias_idx, ordered, country = _load()
    f = _PARENS.sub("", frag).strip()
    f = _OPENP.sub("", f).strip()       # 拆断的"未知（…"残留
    f = _SUFFIX.sub("", f).strip()
    if not f:
        return None
    nf = _norm(f)
    # 噪声:精确命中,或以噪声词开头(如 "未知（作者…" 拆碎后)
    if not nf or nf in drop or any(nf.startswith(d) for d in drop):
        return None
    # 1) 精确
    if nf in alias_idx:
        c = alias_idx[nf]
        return c, country.get(c, "unknown")
    # 2) 子串(长别名优先):别名出现在片段里,或片段出现在别名里
    for alias_n, canon in ordered:
        if len(alias_n) < 2:
            continue
        if alias_n in nf or (len(nf) >= 2 and nf in alias_n):
            return canon, country.get(canon, "unknown")
    # 3) 兜底:保留清理后的原片段,暂不合并(国家未知)
    if nf in drop:
        return None
    return f, "unknown"


@lru_cache(maxsize=4096)
def resolve(org_raw):
    """org 原始串 → [(canonical, country), …](已去重保序,空则 [])。

    复合机构拆成多个;噪声丢弃;字典外片段保留清理后的原名。
    """
    if not org_raw:
        return ()
    drop, *_ = _load()
    whole = _norm(_OPENP.sub("", _PARENS.sub("", org_raw)))
    if not whole or whole in drop or any(whole.startswith(d) for d in drop):
        return ()                       # 整条是"未知…/多机构…"说明文,不拆
    out, seen = [], set()
    for frag in _SPLIT.split(org_raw):
        r = _resolve_fragment(frag)
        if r and r[0] not in seen:
            seen.add(r[0])
            out.append(r)
    return tuple(out)


def primary(org_raw):
    """主机构(第一个规范机构)的 (canonical, country);无则 ('', '')。"""
    r = resolve(org_raw)
    return r[0] if r else ("", "")


if __name__ == "__main__":  # 自检
    for s in ["CMU & Meta", "Google DeepMind/斯坦福大学", "英伟达", "NVIDIA GEAR Lab",
              "UC Berkeley / CMU", "多机构", "未知（作者单位未披露）", "清华大学/中科院自动化所联合",
              "斯坦福", "Stanford & NVIDIA", "哥伦比亚大学/NVIDIA"]:
        print(f"{s!r:45} -> {list(resolve(s))}")
