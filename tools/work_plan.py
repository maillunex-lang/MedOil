#!/usr/bin/env python3
"""Simple dependency-aware roadmap for Industrial Empire. Python 3.10+, no external dependencies."""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tasks" / "tasks.json"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
VALID = {"planned", "in_progress", "blocked", "done"}

def load():
    return json.loads(SOURCE.read_text(encoding="utf-8"))

def validate(data):
    tasks = data["tasks"]
    ids = [t["id"] for t in tasks]
    if len(ids) != 66 or len(set(ids)) != len(ids):
        raise ValueError("Expected 66 unique tasks")
    lookup = {t["id"]: t for t in tasks}
    visiting, visited = set(), set()
    def visit(task_id):
        if task_id in visiting:
            raise ValueError("Dependency cycle at " + task_id)
        if task_id in visited:
            return
        visiting.add(task_id)
        for dep in lookup[task_id]["depends_on"]:
            if dep not in lookup:
                raise ValueError("Missing dependency " + dep)
            visit(dep)
        visiting.remove(task_id)
        visited.add(task_id)
    for t in tasks:
        if t["status"] not in VALID:
            raise ValueError("Invalid status: " + t["id"])
        if t["status"] == "done" and (not t.get("pr") or not re.fullmatch(r"[a-fA-F0-9]{40}", str(t.get("merge_sha") or ""))):
            raise ValueError("Done needs merged PR and 40-character SHA: " + t["id"])
        if t["status"] == "done" and any(lookup[d]["status"] != "done" for d in t["depends_on"]):
            raise ValueError("Done task has unfinished dependency: " + t["id"])
        visit(t["id"])
    return lookup

def ready(data):
    lookup = validate(data)
    return [t for t in data["tasks"] if t["status"] == "planned" and all(lookup[d]["status"] == "done" for d in t["depends_on"])]

def render(data):
    lookup = validate(data)
    total = len(data["tasks"])
    done = sum(t["status"] == "done" for t in data["tasks"])
    out = ["# Industrial Empire: дорожная карта", "", "> Генерируется из tasks/tasks.json. Не редактировать вручную.", "", f"**Готово: {done}/{total}.**", "", "## Следующие доступные задачи", ""]
    next_tasks = ready(data)
    out.extend([f"- **{t['id']}** {t['title']}" for t in next_tasks] or ["- Нет доступных задач. Проверьте блокировки и PR."])
    for stream in ["S0","A","B","C","D","E","I"]:
        out += ["", f"## {stream}", ""]
        for t in data["tasks"]:
            if t["stream"] != stream:
                continue
            symbol = "x" if t["status"] == "done" else " "
            deps = ", ".join(t["depends_on"]) or "нет"
            out.append(f"- [{symbol}] **{t['id']}** {t['title']} | {t['status']} | зависимости: {deps}" + (f" | PR #{t['pr']}" if t.get("pr") else ""))
    return "\n".join(out) + "\n"

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ["next","validate","build"]:
        sub.add_parser(name)
    show = sub.add_parser("show"); show.add_argument("id")
    set_cmd = sub.add_parser("set")
    set_cmd.add_argument("id")
    set_cmd.add_argument("status", choices=sorted(VALID))
    set_cmd.add_argument("--pr", type=int)
    set_cmd.add_argument("--sha")
    args = parser.parse_args()
    data = load()
    lookup = validate(data)
    if args.cmd == "validate":
        print(f"OK: {len(lookup)} tasks, no cycles, statuses valid")
    elif args.cmd == "next":
        for t in ready(data):
            print(t["id"], t["title"])
    elif args.cmd == "show":
        if args.id not in lookup:
            parser.error("Unknown task ID")
        print(json.dumps(lookup[args.id], ensure_ascii=False, indent=2))
    elif args.cmd == "build":
        ROADMAP.write_text(render(data), encoding="utf-8")
        print("Updated", ROADMAP)
    elif args.cmd == "set":
        if args.id not in lookup:
            parser.error("Unknown task ID")
        t = lookup[args.id]
        if args.status == "done":
            if any(lookup[d]["status"] != "done" for d in t["depends_on"]):
                parser.error("Dependencies not done")
            if not args.pr or not args.sha or not re.fullmatch(r"[a-fA-F0-9]{40}", args.sha):
                parser.error("done requires --pr NUMBER --sha 40_HEX_MERGE_SHA")
            t["pr"], t["merge_sha"] = args.pr, args.sha.lower()
        t["status"] = args.status
        validate(data)
        SOURCE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        ROADMAP.write_text(render(data), encoding="utf-8")
        print("Updated", args.id, args.status)
if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
