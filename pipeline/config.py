"""加载 config.yaml。"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.yaml"
ENV_PATH = ROOT / ".env"


def load_env(path=ENV_PATH):
    """零依赖加载 .env(KEY=VALUE,# 注释),不覆盖已存在的环境变量。
    CI 里走 GitHub secret(无 .env 文件),本地走 .env —— 两边都不用改代码。"""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


def load_config(path=CONFIG_PATH):
    load_env()
    try:
        import yaml
    except ImportError:
        raise SystemExit("缺少 PyYAML,请先 `pip install pyyaml`(这是唯一硬依赖)")
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


def enabled_routes(cfg):
    return [r for r in cfg.get("routes", []) if r.get("enabled", True)]
