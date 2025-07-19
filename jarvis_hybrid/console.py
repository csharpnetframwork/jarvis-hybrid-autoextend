"""
Jarvis Hybrid Console (Auto-Extend)
"""
from __future__ import annotations
import os
from .agent import Agent
from .config import load_config, save_config
from .logger import set_console_echo
from .chat import chat_loop
from .scan import scan_project_fast
from .ollama_client import model_generate
from . import memory
from . import extension_manager as XM

def clear(): os.system("cls" if os.name=="nt" else "clear")
def pause(): input("\nPress Enter...")
def banner():
    print("="*60); print(" Jarvis Hybrid Console ".center(60,"=")); print("="*60)

def menu():
    print("\nMain Menu")
    print("1. Add Goal")
    print("2. Show Goals")
    print("3. Run Goals")
    print("4. Learning Mode (scan + summarize)")
    print("5. Search Memory")
    print("6. Settings")
    print("7. Toggle Log Echo")
    print("8. Chat with Assistant")
    print("9. Manage Learned Actions")  # NEW
    print("10. Exit")

def settings_menu(cfg):
    while True:
        clear(); banner()
        print("Model:", cfg.model)
        print("Console Echo:", cfg.console_echo)
        print("Allow System Actions:", cfg.allow_system_actions)
        print("Allow Web Open:", cfg.allow_web_open)
        print("\nAllowed Roots:")
        for i,r in enumerate(cfg.allowed_roots,1):
            print(f" {i}. {r}")
        print("\n1. Add Root")
        print("2. Change Model")
        print("3. Toggle System Actions")
        print("4. Toggle Web Open")
        print("5. Back")
        ch = input("> ").strip()
        if ch=="1":
            newr = input("Enter full folder path: ").strip()
            if newr: cfg.allowed_roots.append(newr)
        elif ch=="2":
            cfg.model = input("New model name: ").strip() or cfg.model
        elif ch=="3":
            cfg.allow_system_actions = not cfg.allow_system_actions
        elif ch=="4":
            cfg.allow_web_open = not cfg.allow_web_open
        elif ch=="5":
            save_config(cfg); break

def learning_mode(cfg):
    clear(); banner()
    path = input("Project root: ").strip()
    if not path: pause(); return
    if not any(path.lower().startswith(ar.lower()) for ar in cfg.allowed_roots):
        print("Path not allowed. Add in Settings."); pause(); return
    print("Scanning...")
    listing = scan_project_fast(path)
    print("\nSummarizing...")
    summary = model_generate(cfg.model, f'Summarize this project structure:\n{listing}\nSummary:')
    print("\n=== Summary ===\n")
    print(summary)
    memory.add_project_summary(path, summary)
    pause()

def memory_search():
    clear(); banner()
    q=input("Search memory: ").strip()
    if not q: pause(); return
    hits = memory.search_text(q)
    print("\nResults:")
    for sc,txt in hits:
        print("-", txt[:120])
    pause()

def manage_extensions_menu():
    while True:
        clear(); banner()
        print("Learned Actions Manager")
        print("1. List Approved Extensions")
        print("2. List Pending Extensions")
        print("3. Approve Pending -> Extension")
        print("4. Delete Pending")
        print("5. Back")
        ch=input("> ").strip()
        if ch=="1":
            exts = XM.list_extensions()
            print("\nApproved Extensions:")
            if exts:
                for i,e in enumerate(exts,1):
                    print(f"{i}. {e['name']} triggers={e['triggers']} file={e['path']}")
            else:
                print("(none)")
            pause()
        elif ch=="2":
            pend = XM.list_pending()
            print("\nPending Extensions:")
            if pend:
                for i,e in enumerate(pend):
                    print(f"[{i}] goal={e['goal'][:60]}...")
            else:
                print("(none)")
            pause()
        elif ch=="3":
            pend = XM.list_pending()
            if not pend:
                print("No pending."); pause(); continue
            idx = input("Enter pending index to approve: ").strip()
            if not idx.isdigit():
                print("Invalid."); pause(); continue
            idx = int(idx)
            goal = pend[idx]["goal"] if 0 <= idx < len(pend) else ""
            print(f"Goal: {goal}")
            trig_raw = input("Enter comma-separated triggers (keywords): ").strip()
            triggers = [t.strip() for t in trig_raw.split(",") if t.strip()] or [goal]
            name = input("Short name for extension: ").strip() or goal[:30]
            msg = XM.promote_pending(idx, triggers, name=name)
            print(msg); pause()
        elif ch=="4":
            pend = XM.list_pending()
            if not pend:
                print("No pending."); pause(); continue
            idx = input("Enter pending index to delete: ").strip()
            if not idx.isdigit():
                print("Invalid."); pause(); continue
            idx = int(idx)
            pend = XM.list_pending()
            if 0 <= idx < len(pend):
                pend.pop(idx)
                XM.save_pending(pend)
                print("Deleted."); pause()
            else:
                print("Out of range."); pause()
        elif ch=="5":
            break

def main():
    agent = Agent()
    cfg = load_config()
    set_console_echo(cfg.console_echo)
    while True:
        clear(); banner(); menu()
        ch = input("> ").strip()
        if ch=="1":
            g=input("Goal: ").strip(); agent.add_goal(g)
        elif ch=="2":
            print("\nGoals:"); 
            if agent.goals:
                for i,g in enumerate(agent.goals,1): print(f"{i}. {g}")
            else: print("(none)")
            pause()
        elif ch=="3":
            agent.process_goals(); pause()
        elif ch=="4":
            learning_mode(cfg)
        elif ch=="5":
            memory_search()
        elif ch=="6":
            settings_menu(cfg)
        elif ch=="7":
            cfg.console_echo = not cfg.console_echo
            set_console_echo(cfg.console_echo)
            print("Console echo:", cfg.console_echo); pause()
        elif ch=="8":
            clear(); banner(); chat_loop(); pause()
        elif ch=="9":
            manage_extensions_menu()
        elif ch=="10":
            save_config(cfg); break

if __name__=="__main__":
    main()
