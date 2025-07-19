"""
Jarvis Hybrid Memory (SQLite)
"""
from __future__ import annotations
import sqlite3, time
from pathlib import Path
from typing import List, Tuple

DB_PATH = Path(__file__).resolve().parent.parent / "memory.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS goals(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 text TEXT NOT NULL,
 ts REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS project_summaries(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 root TEXT NOT NULL,
 summary TEXT NOT NULL,
 ts REAL NOT NULL
);
"""

def connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = connect(); cur = conn.cursor(); cur.executescript(SCHEMA); conn.commit(); conn.close()
init_db()

def add_goal(text: str):
    conn = connect(); cur = conn.cursor()
    cur.execute("INSERT INTO goals(text,ts) VALUES(?,?)",(text,time.time()))
    conn.commit(); conn.close()

def list_goals():
    conn = connect(); cur = conn.cursor()
    cur.execute("SELECT id,text,ts FROM goals ORDER BY id DESC")
    rows = cur.fetchall(); conn.close(); return rows

def clear_goals():
    conn = connect(); cur = conn.cursor()
    cur.execute("DELETE FROM goals"); conn.commit(); conn.close()

def add_project_summary(root: str, summary: str):
    conn = connect(); cur = conn.cursor()
    cur.execute("INSERT INTO project_summaries(root,summary,ts) VALUES(?,?,?)",(root,summary,time.time()))
    conn.commit(); conn.close()

def search_text(q: str, topk=10):
    conn = connect(); cur = conn.cursor()
    cur.execute("SELECT summary FROM project_summaries")
    rows = cur.fetchall(); conn.close()
    ql = q.lower(); scored=[]
    for (txt,) in rows:
        scored.append((txt.lower().count(ql), txt))
    scored.sort(reverse=True, key=lambda x:x[0])
    return scored[:topk]
