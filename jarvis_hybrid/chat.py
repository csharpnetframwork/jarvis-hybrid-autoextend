"""
Chat with Assistant (multi-turn context)
"""
from __future__ import annotations
from typing import List, Tuple
from .config import load_config
from .ollama_client import model_generate
from .logger import log

MAX_TURNS = 12

def _build_prompt(history: List[Tuple[str,str]], user: str) -> str:
    lines=[]
    for u,a in history[-MAX_TURNS:]:
        lines.append(f"User: {u}")
        lines.append(f"Assistant: {a}")
    lines.append(f"User: {user}")
    lines.append("Assistant:")
    return "\n".join(lines)

def chat_loop():
    cfg = load_config()
    hist: List[Tuple[str,str]]=[]
    print("=== Jarvis Chat ===")
    print("Type 'exit' to return.\n")
    while True:
        u = input("You: ").strip()
        if u.lower() in ("exit","quit","q"): break
        if not u: continue
        log(f"[CHAT][USER] {u}")
        prompt = _build_prompt(hist,u)
        a = model_generate(cfg.model, prompt).strip()
        if not a: a="(no response)"
        print(f"Assistant: {a}\n")
        log(f"[CHAT][ASSISTANT] {a}")
        hist.append((u,a))
