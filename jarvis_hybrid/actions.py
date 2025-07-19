"""
Known actions for fast execution.
"""
from __future__ import annotations
import os, webbrowser, subprocess, psutil
from pathlib import Path
from typing import Optional
from .logger import log
from .config import load_config

def _in_allowed(path: Path, allowed) -> bool:
    pl = str(path.resolve()).lower()
    for ar in allowed:
        if pl.startswith(str(Path(ar).resolve()).lower()):
            return True
    return False

def run_action(goal: str) -> str:
    cfg = load_config()
    g = goal.lower()

    # open websites
    if cfg.allow_web_open and ("youtube" in g or "open youtube" in g):
        webbrowser.open("https://www.youtube.com"); return "Opened YouTube."
    if cfg.allow_web_open and ("google" in g or "open google" in g or "search google" in g):
        webbrowser.open("https://www.google.com"); return "Opened Google."

    # open system apps
    if cfg.allow_system_actions and "notepad" in g:
        subprocess.Popen(["notepad.exe"]); return "Opened Notepad."
    if cfg.allow_system_actions and ("calc" in g or "calculator" in g):
        subprocess.Popen(["calc.exe"]); return "Opened Calculator."
    if cfg.allow_system_actions and ("cmd" in g or "command prompt" in g):
        subprocess.Popen(["cmd.exe"]); return "Opened Command Prompt."
    if cfg.allow_system_actions and "powershell" in g:
        subprocess.Popen(["powershell.exe"]); return "Opened PowerShell."
    if cfg.allow_system_actions and "vs code" in g or "vscode" in g or "code " in g:
        subprocess.Popen(["code"]); return "Tried to open VS Code (requires code in PATH)."

    # create note file
    if "create note" in g:
        fname = "note.txt"
        with open(fname,"a",encoding="utf-8") as fh: fh.write("New note.\n")
        os.startfile(fname)
        return f"Created and opened {fname}."

    # read file if allowed
    if g.startswith("read file "):
        p = Path(goal.split(" ",2)[2].strip().strip('"').strip("'"))
        if not p.exists(): return f"File not found: {p}"
        if not _in_allowed(p, cfg.allowed_roots): return f"Blocked (not in allowed roots): {p}"
        try:
            txt = p.read_text(encoding="utf-8",errors="ignore")
            return f"--- Begin {p.name} ---\n{txt[:2000]}\n--- End ---"
        except Exception as e:
            return f"Read error: {e}"

    # system info
    if "battery" in g:
        try:
            b = psutil.sensors_battery()
            if b is None: return "No battery info."
            return f"Battery: {b.percent}% | Plugged: {b.power_plugged}"
        except Exception as e:
            return f"Battery read error: {e}"
    if "cpu usage" in g or "cpu" in g:
        try:
            return f"CPU Usage: {psutil.cpu_percent(interval=1.0)}%"
        except Exception as e:
            return f"CPU read error: {e}"

    return ""  # unknown -> let planner/LLM handle
