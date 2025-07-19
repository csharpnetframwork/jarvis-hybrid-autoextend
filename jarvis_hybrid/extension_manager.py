"""
Extension Manager
=================
Persist & reuse AI-generated Python actions ("extensions").

Locations:
- extensions/               -> folder of approved extension scripts
- extensions/extension_index.json -> registry of extensions [{name, triggers, path, created_ts}]

Pending:
- extensions/pending_extensions.json -> queue of AI-generated code awaiting user approval.

Usage:
    from . import extension_manager as XM
    ext = XM.find_matching_extension(goal)
    if ext: XM.run_extension(ext, context={...})

    XM.queue_pending(goal, code_str)
    XM.promote_pending(idx, triggers=[...])  # user approves

Security:
- Only runs scripts saved in extensions dir.
- Paths normalized; no absolute injection.
"""
from __future__ import annotations
import json, os, subprocess, sys, time
from pathlib import Path
from typing import List, Dict, Optional

PKG_DIR = Path(__file__).resolve().parent
EXT_DIR = PKG_DIR.parent / "extensions"
EXT_DIR.mkdir(exist_ok=True)

INDEX_PATH = EXT_DIR / "extension_index.json"
PENDING_PATH = EXT_DIR / "pending_extensions.json"

# ------------------ persistence ------------------
def _load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default

def _save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def load_index() -> List[Dict]:
    return _load_json(INDEX_PATH, [])

def save_index(idx: List[Dict]):
    _save_json(INDEX_PATH, idx)

def load_pending() -> List[Dict]:
    return _load_json(PENDING_PATH, [])

def save_pending(pend: List[Dict]):
    _save_json(PENDING_PATH, pend)

# ------------------ queue pending ------------------
def queue_pending(goal: str, code: str):
    pend = load_pending()
    pend.append({
        "goal": goal,
        "code": code,
        "created_ts": time.time()
    })
    save_pending(pend)

# ------------------ promote pending -> extension ------------------
def promote_pending(i: int, triggers: List[str], name: Optional[str]=None) -> str:
    pend = load_pending()
    if i < 0 or i >= len(pend):
        return "Invalid pending index."
    item = pend.pop(i)
    save_pending(pend)
    code = item["code"]
    goal = item["goal"]
    if not name:
        name = goal[:40]
    # slug filename
    safe = "".join(c if c.isalnum() else "_" for c in name)[:40] or "ext"
    ext_path = EXT_DIR / f"{safe}.py"
    ext_path.write_text(code, encoding="utf-8")

    idx = load_index()
    idx.append({
        "name": name,
        "triggers": triggers,
        "path": str(ext_path.name),
        "created_ts": time.time()
    })
    save_index(idx)
    return f"Extension saved: {ext_path.name}"

# ------------------ list extensions / pending ------------------
def list_extensions() -> List[Dict]:
    return load_index()

def list_pending() -> List[Dict]:
    return load_pending()

# ------------------ match goal to extension ------------------
def find_matching_extension(goal: str) -> Optional[Dict]:
    g = goal.lower()
    for ext in load_index():
        for t in ext.get("triggers",[]):
            if t.lower() in g:
                return ext
    return None

# ------------------ run extension ------------------
def run_extension(ext: Dict, timeout=60) -> str:
    pyfile = EXT_DIR / ext["path"]
    if not pyfile.exists():
        return f"Extension file missing: {pyfile}"
    try:
        proc = subprocess.run(
            [sys.executable, str(pyfile)],
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="ignore"
        )
        return (proc.stdout or "") + (proc.stderr or "")
    except Exception as e:
        return f"Extension run error: {e}"
