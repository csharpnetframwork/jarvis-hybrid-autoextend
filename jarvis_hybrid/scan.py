"""
Fast scan for Learning Mode.
"""
from __future__ import annotations
import os
from pathlib import Path
from .config import load_config
from .logger import log

TEXT_EXT = {".py",".md",".txt",".json",".yaml",".yml",".ini",".cfg",".toml",".xml",".html",".js",".css",".ts",".csv",".sql",".java",".cs",".cpp",".c",".hpp",".h",".go",".rs",".php",".ps1",".bat",".sh"}

def scan_project_fast(root_path: str) -> str:
    cfg = load_config()
    root = Path(root_path)
    if not root.exists():
        return f"Path not found: {root_path}"
    allowed = any(str(root).lower().startswith(str(Path(ar)).lower()) for ar in cfg.allowed_roots)
    if not allowed:
        return f"Path not allowed: {root_path}"
    listing=[]
    for dirpath, dirs, files in os.walk(root):
        # ignore hidden dirs and heavy known names
        dirs[:] = [d for d in dirs if d not in ("node_modules",".git","__pycache__", "dist","build",".venv","venv","env")]
        for fn in files:
            p = Path(dirpath)/fn
            try:
                size = p.stat().st_size
            except Exception:
                continue
            kind = "binary"
            if p.suffix.lower() in TEXT_EXT and size < 5_000_000:
                kind = "text"
            rel = p.relative_to(root)
            listing.append(f"{rel} | {kind} | {size} bytes")
            # no DB indexing here; done in learning_mode
    return "\n".join(listing[:5000])
