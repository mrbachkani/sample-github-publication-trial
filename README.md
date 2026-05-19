# Branch Isolation Trial CLI

A tiny Python CLI that stores short messages in JSON.

## Features
- Add item: `python -m src.main add "hello"`
- List items: `python -m src.main list`
- JSON storage
- Mark done: `python -m src.main done 0`
- Clear completed: `python -m src.main clear-completed`
- Clear all: `python -m src.main clear`
- Delete by index: `python -m src.main delete 0`
- Edit by index: `python -m src.main edit 0 "new text"`
- Due dates: `python -m src.main add "task" --due 2026-05-20`
- Priority: `python -m src.main add "task" --priority high`
- JSON output: `python -m src.main list --json`
- Count items: `python -m src.main count`
- Item count: `python -m src.main item-count` (prints total number of stored items)
- Check if empty: `python -m src.main empty` (prints whether store has zero items)
- Filter by status: `python -m src.main list --status pending` or `--status completed`
- Filter by priority: `python -m src.main list --priority high`
- Filter by due date: `python -m src.main list --due-before 2026-05-31`
- Sort results: `python -m src.main list --sort due` or `--sort priority` or `--sort id`
- Combined filters: `python -m src.main list --status pending --priority high --sort due`
- Search items: `python -m src.main search "query"` (case-insensitive substring)
- Has items: `python -m src.main has-items` (prints total number of stored items)
- Export to JSON: `python -m src.main export` (writes all tasks to `asks_export.json`)
- Import from JSON: `python -m src.main import tasks.json` (imports tasks from a JSON file)
- Item summary: `python -m src.main item-summary` (prints total and completed item counts)
- Completed count: `python -m src.main completed-count` (prints number of completed tasks)
- Pending count: `python -m src.main pending-count` (prints number of pending tasks)
