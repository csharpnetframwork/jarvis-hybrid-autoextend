"""
Jarvis Hybrid Agent (Auto-Extend)
---------------------------------
Flow:
 1. Try known rule-based action (fast).
 2. Check saved extensions (user-approved learned actions).
 3. If no match -> LLM planner -> Python code -> run.
 4. Queue generated code as pending extension for user review.
"""
from __future__ import annotations
from typing import Callable, List
from .logger import log
from .config import load_config
from . import memory
from .actions import run_action
from .planner import plan
from .code_exec import run_python
from . import extension_manager as XM

LogFn = Callable[[str], None]

class Agent:
    def __init__(self, cb: LogFn | None = None):
        self.cb = cb or (lambda m: None)
        self.cfg = load_config()
        self.goals: List[str] = []

    def _emit(self, msg: str, level="INFO"):
        log(msg, level); self.cb(msg)

    def add_goal(self, g: str):
        g = g.strip()
        if not g: return
        self.goals.append(g)
        memory.add_goal(g)
        self._emit(f"Added goal: {g}")

    def clear_goals(self):
        self.goals.clear()
        memory.clear_goals()
        self._emit("Goals cleared.")

    def _handle_goal(self, goal: str):
        # 1. Known action
        act_result = run_action(goal)
        if act_result:
            self._emit(f"Action result: {act_result}")
            return

        # 2. Extension match
        ext = XM.find_matching_extension(goal)
        if ext:
            self._emit(f"Using learned extension: {ext['name']}")
            out = XM.run_extension(ext)
            self._emit(out)
            return

        # 3. Plan via LLM
        self._emit(f"Planning goal: {goal}")
        pl = plan(goal, self.cfg.model)
        self._emit(f"Planner intent: {pl.get('intent')} target={pl.get('target')}")
        code = pl.get("python_code","") or ""
        if code.strip():
            self._emit("Running LLM-generated Python...")
            out = run_python(code)
            self._emit(out)
            # 4. Queue for extension approval
            XM.queue_pending(goal, code)
            self._emit("Generated code queued for extension review.")
        else:
            self._emit("No code from planner; nothing to do.")

    def process_goals(self):
        for g in list(self.goals):
            self._emit(f"[DEBUG] Processing goal: {g}")
            self._handle_goal(g)
        self.goals.clear()
        self._emit("All goals complete.")
