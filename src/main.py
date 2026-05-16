"""Tiny todo CLI with JSON storage."""

import argparse
import json
import sys
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent.parent / "todos.json"


def load() -> list:
    if DB_FILE.exists():
        with open(DB_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def save(todos: list):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2)


def cmd_add(args):
    todos = load()
    entry = {"task": args.task, "done": False}
    if args.priority:
        entry["priority"] = args.priority
    if args.due:
        entry["due"] = args.due
    todos.append(entry)
    save(todos)
    print(f'Added: "{args.task}"')


def _validate_list_args(args):
    if getattr(args, "status", None):
        if args.status not in ("pending", "completed"):
            print(f'Error: invalid status "{args.status}". Choose: pending, completed', file=sys.stderr)
            sys.exit(1)
    if getattr(args, "priority", None):
        if args.priority not in ("high", "medium", "low"):
            print(f'Error: invalid priority "{args.priority}". Choose: high, medium, low', file=sys.stderr)
            sys.exit(1)
    if getattr(args, "sort", None):
        if args.sort not in ("due", "priority", "id"):
            print(f'Error: invalid sort "{args.sort}". Choose: due, priority, id', file=sys.stderr)
            sys.exit(1)
    if getattr(args, "due_before", None):
        from datetime import datetime
        try:
            datetime.strptime(args.due_before, "%Y-%m-%d")
        except ValueError:
            print(f'Error: invalid date "{args.due_before}". Use YYYY-MM-DD', file=sys.stderr)
            sys.exit(1)


def cmd_list(args):
    _validate_list_args(args)
    todos = load()

    # Filter by status
    if getattr(args, "status", None):
        if args.status == "pending":
            todos = [t for t in todos if not t.get("done")]
        else:
            todos = [t for t in todos if t.get("done")]

    # Filter by priority
    if getattr(args, "priority", None):
        todos = [t for t in todos if t.get("priority") == args.priority]

    # Filter by due-before
    if getattr(args, "due_before", None):
        todos = [t for t in todos if "due" in t and t["due"] <= args.due_before]

    # Sort
    if getattr(args, "sort", None) and args.sort != "id":
        if args.sort == "due":
            has_due = [t for t in todos if "due" in t]
            no_due = [t for t in todos if "due" not in t]
            has_due.sort(key=lambda t: t["due"])
            todos = has_due + no_due
        elif args.sort == "priority":
            order = {"high": 0, "medium": 1, "low": 2}
            with_pri = [t for t in todos if "priority" in t]
            no_pri = [t for t in todos if "priority" not in t]
            with_pri.sort(key=lambda t: order.get(t["priority"], 3))
            todos = with_pri + no_pri

    if getattr(args, "json", False):
        print(json.dumps(todos, indent=2))
        return
    if not todos:
        print("No tasks.")
        return
    for i, t in enumerate(todos):
        status = "x" if t.get("done") else " "
        extra = ""
        if "due" in t:
            extra += f' due={t["due"]}'
        if "priority" in t:
            extra += f' pri={t["priority"]}'
        print(f'  [{i}] [{status}] {t["task"]}{extra}')


def cmd_done(args):
    todos = load()
    try:
        idx = int(args.id)
    except ValueError:
        print("Error: invalid task ID", file=sys.stderr)
        sys.exit(1)
    if idx < 0 or idx >= len(todos):
        print("Error: invalid task ID", file=sys.stderr)
        sys.exit(1)
    todos[idx]["done"] = True
    save(todos)
    print(f'Marked task {idx} as done.')


def cmd_clear_completed(args):
    todos = load()
    todos = [t for t in todos if not t.get("done")]
    save(todos)
    print("Cleared completed tasks.")


def cmd_delete(args):
    todos = load()
    try:
        idx = int(args.id)
    except ValueError:
        print("Error: invalid task ID", file=sys.stderr)
        sys.exit(1)
    if idx < 0 or idx >= len(todos):
        print("Error: invalid task ID", file=sys.stderr)
        sys.exit(1)
    todos.pop(idx)
    save(todos)
    print(f'Deleted task {idx}.')


def cmd_edit(args):
    todos = load()
    try:
        idx = int(args.id)
    except ValueError:
        print("Error: invalid task ID", file=sys.stderr)
        sys.exit(1)
    if idx < 0 or idx >= len(todos):
        print("Error: invalid task ID", file=sys.stderr)
        sys.exit(1)
    todos[idx]["task"] = args.text
    save(todos)
    print(f'Edited task {idx}.')


def cmd_clear(args):
    save([])
    print("Cleared all items.")


def cmd_count(args):
    todos = load()
    total = len(todos)
    done = sum(1 for t in todos if t.get("done"))
    print(f'Total items: {total}')
    print(f'Done: {done}')


def cmd_search(args):
    todos = load()
    query = args.query.lower()
    matches = [t for t in todos if query in t["task"].lower()]
    if not matches:
        print(f"No items matched '{args.query}'.")
        return
    for i, t in enumerate(matches):
        status = "x" if t.get("done") else " "
        extra = ""
        if "due" in t:
            extra += f' due={t["due"]}'
        if "priority" in t:
            extra += f' pri={t["priority"]}'
        print(f'  [{i}] [{status}] {t["task"]}{extra}')


def main():
    parser = argparse.ArgumentParser(description="Tiny todo CLI")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add")
    p_add.add_argument("task")
    p_add.add_argument("--priority")
    p_add.add_argument("--due")

    p_list = sub.add_parser("list")
    p_list.add_argument("--json", action="store_true")
    p_list.add_argument("--status")
    p_list.add_argument("--priority")
    p_list.add_argument("--due-before", dest="due_before")
    p_list.add_argument("--sort")

    p_done = sub.add_parser("done")
    p_done.add_argument("id")

    sub.add_parser("clear-completed")

    p_delete = sub.add_parser("delete")
    p_delete.add_argument("id")

    p_edit = sub.add_parser("edit")
    p_edit.add_argument("id")
    p_edit.add_argument("text")

    sub.add_parser("clear")
    sub.add_parser("count")

    p_search = sub.add_parser("search")
    p_search.add_argument("query")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {"add": cmd_add, "list": cmd_list, "done": cmd_done,
     "clear-completed": cmd_clear_completed, "delete": cmd_delete,
     "edit": cmd_edit, "clear": cmd_clear, "count": cmd_count, "search": cmd_search}[args.command](args)


if __name__ == "__main__":
    main()
