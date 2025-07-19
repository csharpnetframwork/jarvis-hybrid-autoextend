"""
Planner - interpret user goal into structured plan.
"""
from __future__ import annotations
import json
from .ollama_client import model_generate

PROMPT_TEMPLATE = """You are an automation agent on Windows.
Classify the user goal and return JSON:
{
 "intent": "open_url|open_app|create_file|read_file|system_info|python|other",
 "target": "string or null",
 "python_code": "optional python code to achieve goal if needed"
}
Goal: {goal}
Return ONLY JSON.
"""

def plan(goal: str, model: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(goal=goal)
    out = model_generate(model, prompt)
    try:
        start = out.index("{")
        return json.loads(out[start:])
    except Exception:
        return {"intent":"other","target":goal,"python_code":""}
