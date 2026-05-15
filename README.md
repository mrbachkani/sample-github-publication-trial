# Branch Isolation Trial CLI

A tiny Python CLI that stores short messages in JSON.

## Features
- Add item: `python -m src.main add "hello"`
- List items: `python -m src.main list`
- JSON storage
- Mark done: `python -m src.main done 0`
- Clear completed: `python -m src.main clear-completed`
- Delete by index: `python -m src.main delete 0`
- Edit by index: `python -m src.main edit 0 "new text"`
- Due dates: `python -m src.main add "task" --due 2026-05-20`
- Priority: `python -m src.main add "task" --priority high`
- JSON output: `python -m src.main list --json`
- Count items: `python -m src.main count`
