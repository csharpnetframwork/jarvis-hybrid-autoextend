"""
Jarvis Hybrid Logger
Batched async logging -> logs/jarvis.log
"""
from __future__ import annotations
import queue, threading, time
from pathlib import Path
from datetime import datetime

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "jarvis.log"
MAX_BYTES = 5 * 1024 * 1024

_q: "queue.Queue[str]" = queue.Queue()
_echo = True
_stop = False

def set_console_echo(v: bool):
    global _echo
    _echo = v

def _rotate():
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > MAX_BYTES:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        LOG_FILE.rename(LOG_FILE.with_name(f"jarvis_{ts}.log"))

def _writer():
    global _stop
    buf = []
    last = time.time()
    while not _stop or not _q.empty():
        try:
            ln = _q.get(timeout=0.25)
            buf.append(ln)
        except queue.Empty:
            pass
        if buf and (len(buf) >= 100 or time.time() - last > 0.5):
            _rotate()
            with open(LOG_FILE, "a", encoding="utf-8", errors="ignore") as fh:
                fh.writelines(buf)
            if _echo:
                for l in buf:
                    print(l, end="")
            buf.clear()
            last = time.time()

_thread = threading.Thread(target=_writer, daemon=True)
_thread.start()

def log(msg: str, level: str="INFO"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    _q.put(f"{ts} [{level}] {msg}\n")

def close_logger():
    global _stop
    _stop = True
    _thread.join(timeout=2)
