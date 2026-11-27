"""排序系数:从 agent/weights.yaml 读(缺文件/缺项用默认值)。系数集中在一处,
编辑 agent 调权重只改那个 yaml,管线和页面都跟着变。"""
from functools import lru_cache
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "agent" / "weights.yaml"
DEFAULT = {
    "version": 0,
    "votes": {"hf_upvote": 1.0, "github_star": 0.05, "citation": 4.0, "venue_accept": 10,
              "awards": {"Best Paper": 250, "Best Paper Finalist": 100, "Oral": 60,
                         "Spotlight": 40, "Highlight": 40}},
    "heat": {"scale": 25, "half": 10},
    "combo": {"power": 3},
    "quota": {"S": 0.06, "A": 0.20},
    "old_repo_days": 120,
}


def _merge(base, over):
    out = dict(base)
    for k, v in (over or {}).items():
        out[k] = _merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


@lru_cache(maxsize=1)
def load():
    try:
        import yaml
        return _merge(DEFAULT, yaml.safe_load(PATH.read_text(encoding="utf-8")) or {})
    except Exception:
        return DEFAULT
