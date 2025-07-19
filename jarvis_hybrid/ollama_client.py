"""
Ollama Client - HTTP first, CLI fallback
"""
from __future__ import annotations
import json, shutil, subprocess
from typing import Optional
from urllib import request, error
from .logger import log

OLLAMA_URL = "http://localhost:11434/api/generate"

def _ollama_http(model: str, prompt: str) -> Optional[str]:
    data = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = request.Request(OLLAMA_URL, data=data, headers={"Content-Type":"application/json"})
    try:
        with request.urlopen(req, timeout=600) as resp:
            body = resp.read().decode("utf-8","ignore")
        try:
            obj = json.loads(body)
            return obj.get("response","").strip()
        except Exception:
            return body.strip()
    except Exception as e:
        log(f"Ollama HTTP failed: {e}","WARN")
        return None

def _ollama_cli(model: str, prompt: str) -> Optional[str]:
    if not shutil.which("ollama"):
        log("Ollama CLI not found.","WARN")
        return None
    try:
        res = subprocess.run(
            ["ollama","run",model,prompt],
            capture_output=True, text=True, check=True,
            encoding="utf-8", errors="ignore"
        )
        return res.stdout.strip()
    except Exception as e:
        log(f"Ollama CLI error: {e}","ERROR")
        return None

def model_generate(model: str, prompt: str) -> str:
    log(f"Ollama prompt -> {model} ({len(prompt)} chars)")
    out = _ollama_http(model, prompt)
    if out is None:
        out = _ollama_cli(model, prompt)
    if out is None:
        out = "[LLM unavailable]"
    log(f"Ollama response {len(out)} chars")
    return out
