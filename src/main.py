import argparse
import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data.json"


def _load() -> list:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(items: list) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def cmd_add(args):
    items = _load()
    items.append({"text": args.message})
    _save(items)
    print(f"Added: {args.message}")


def cmd_list(args):
    items = _load()
    if not items:
        print("No messages stored.")
        return
    for i, item in enumerate(items, 1):
        print(f"{i}. {item['text']}")


def main():
    parser = argparse.ArgumentParser(
        prog="message-cli",
        description="Store and list short messages in JSON.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "add",
        help="Add a message",
    ).add_argument("message", help="Message text to store")

    subparsers.add_parser("list", help="List all stored messages")

    args = parser.parse_args()

    if args.command == "add":
        cmd_add(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
