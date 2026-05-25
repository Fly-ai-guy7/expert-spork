#!/usr/bin/env python3
"""spork — a tiny CLI todo manager."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

STORE_ENV = "SPORK_FILE"
DEFAULT_STORE = Path.home() / ".spork.json"

PRIORITIES = ("low", "medium", "high")
DEFAULT_PRIORITY = "medium"
_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
_PRIORITY_GLYPH = {"high": "!!", "medium": " ·", "low": "  "}


def store_path() -> Path:
    return Path(os.environ.get(STORE_ENV, DEFAULT_STORE))


def load() -> list[dict]:
    path = store_path()
    if not path.exists():
        return []
    return json.loads(path.read_text())


def save(tasks: list[dict]) -> None:
    store_path().write_text(json.dumps(tasks, indent=2))


def add(text: str, priority: str = DEFAULT_PRIORITY) -> int:
    if priority not in PRIORITIES:
        raise ValueError(f"priority must be one of {PRIORITIES}, got {priority!r}")
    tasks = load()
    next_id = max((t["id"] for t in tasks), default=0) + 1
    tasks.append({"id": next_id, "text": text, "done": False, "priority": priority})
    save(tasks)
    return next_id


def list_tasks() -> list[dict]:
    tasks = load()
    return sorted(
        tasks,
        key=lambda t: (_PRIORITY_RANK.get(t.get("priority", DEFAULT_PRIORITY), 1), t["id"]),
    )


def mark_done(task_id: int) -> bool:
    tasks = load()
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            save(tasks)
            return True
    return False


def remove(task_id: int) -> bool:
    tasks = load()
    kept = [t for t in tasks if t["id"] != task_id]
    if len(kept) == len(tasks):
        return False
    save(kept)
    return True


def clear_done() -> int:
    tasks = load()
    kept = [t for t in tasks if not t["done"]]
    removed = len(tasks) - len(kept)
    if removed:
        save(kept)
    return removed


def format_task(task: dict) -> str:
    mark = "[x]" if task["done"] else "[ ]"
    glyph = _PRIORITY_GLYPH.get(task.get("priority", DEFAULT_PRIORITY), " ·")
    return f"{task['id']:>3} {mark} {glyph} {task['text']}"


def cli_add(args):
    text = " ".join(args.text)
    task_id = add(text, priority=args.priority)
    print(f"added #{task_id} ({args.priority}): {text}")


def cli_list(args):
    tasks = list_tasks()
    if not tasks:
        print("(no tasks)")
        return
    for t in tasks:
        print(format_task(t))


def cli_done(args):
    if mark_done(args.id):
        print(f"done #{args.id}")
    else:
        print(f"no task #{args.id}", file=sys.stderr)
        sys.exit(1)


def cli_remove(args):
    if remove(args.id):
        print(f"removed #{args.id}")
    else:
        print(f"no task #{args.id}", file=sys.stderr)
        sys.exit(1)


def cli_clear(args):
    n = clear_done()
    print(f"cleared {n} completed task(s)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="spork", description="A tiny CLI todo manager.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="add a new task")
    p_add.add_argument("text", nargs="+", help="task description")
    p_add.add_argument(
        "-p", "--priority",
        choices=PRIORITIES,
        default=DEFAULT_PRIORITY,
        help=f"task priority (default: {DEFAULT_PRIORITY})",
    )
    p_add.set_defaults(func=cli_add)

    p_list = sub.add_parser("list", help="list all tasks")
    p_list.set_defaults(func=cli_list)

    p_done = sub.add_parser("done", help="mark a task as done")
    p_done.add_argument("id", type=int)
    p_done.set_defaults(func=cli_done)

    p_remove = sub.add_parser("remove", help="remove a task")
    p_remove.add_argument("id", type=int)
    p_remove.set_defaults(func=cli_remove)

    p_clear = sub.add_parser("clear", help="remove all completed tasks")
    p_clear.set_defaults(func=cli_clear)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
