# utils/config.py
from pathlib import Path
import yaml

DEFAULT = {
    "network": {"replication_factor": 2, "default_bandwidth": 1000},
    "paths": {"data_dir": "./data", "logs_dir": "./logs"},
    "logging": {"level": "INFO", "file": "./logs/trace-music.log"},
    "node": {"heartbeat_interval": 5, "heartbeat_timeout": 15},
}

def load_config(path: str | None = None):
    cfg_path = Path(path) if path else Path(__file__).parent.parent.parent / "config.yaml"
    if not cfg_path.exists():
        return DEFAULT
    with cfg_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    # merge shallowly with default
    merged = DEFAULT.copy()
    merged.update({k: data.get(k, v) for k, v in DEFAULT.items()})
    return merged
