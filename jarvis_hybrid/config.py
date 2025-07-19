"""
Jarvis Hybrid Config
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"

@dataclass
class Config:
    model: str = "mistral"  # faster than llama3 typically
    allowed_roots: List[str] = field(default_factory=list)
    console_echo: bool = True
    allow_system_actions: bool = True   # allow launching apps
    allow_web_open: bool = True         # open browser urls

def load_config() -> Config:
    if CONFIG_PATH.exists():
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        cfg = Config()
        cfg.__dict__.update(data)
        return cfg
    cfg = Config()
    save_config(cfg)
    return cfg

def save_config(cfg: Config):
    CONFIG_PATH.write_text(json.dumps(asdict(cfg), indent=2), encoding="utf-8")
