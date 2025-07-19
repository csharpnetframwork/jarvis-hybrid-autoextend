"""
Execute Python code in subprocess.
"""
from __future__ import annotations
import os, sys, tempfile, subprocess, uuid

def run_python(code: str, timeout=60) -> str:
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, f"jarvis_{uuid.uuid4().hex}.py")
        open(p,"w",encoding="utf-8",errors="ignore").write(code)
        try:
            proc = subprocess.run(
                [sys.executable,p],
                capture_output=True, text=True, timeout=timeout,
                encoding="utf-8", errors="ignore"
            )
            return (proc.stdout or "") + (proc.stderr or "")
        except Exception as e:
            return f"Execution error: {e}"
