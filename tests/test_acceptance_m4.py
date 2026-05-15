"""Acceptance tests for M4.

These tests are generated before implementation and must fail initially (red phase).
After implementation, they must pass (green phase).
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB_FILE = REPO / "todos.json"
README_FILE = REPO / "README.md"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "src.main", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
    )


def setup_function():
    if DB_FILE.exists():
        DB_FILE.unlink()


def teardown_function():
    if DB_FILE.exists():
        DB_FILE.unlink()


def test_m4_delete_edit_json_and_backward_compatibility():
    """Verify delete, edit, --json, invalid task IDs, and backward compatible behavior."""
    DB_FILE.write_text(
        json.dumps([
            {"task": "Legacy task", "done": False},
            {"task": "Pay electricity bill", "done": False, "due": "2026-05-20"},
            {"task": "Fix bug", "done": False, "priority": "high"}
        ]),
        encoding="utf-8",
    )

    listed = run_cli("list", "--json")
    assert listed.returncode == 0, listed.stderr + listed.stdout
    payload = json.loads(listed.stdout)
    assert payload[0]["task"] == "Legacy task"
    assert payload[1]["due"] == "2026-05-20"
    assert payload[2]["priority"] == "high"

    edited = run_cli("edit", "1", "Updated task text")
    assert edited.returncode == 0, edited.stderr + edited.stdout

    deleted = run_cli("delete", "0")
    assert deleted.returncode == 0, deleted.stderr + deleted.stdout

    invalid_delete = run_cli("delete", "99")
    assert invalid_delete.returncode != 0
    assert "invalid task" in (invalid_delete.stdout + invalid_delete.stderr).lower()

    invalid_edit = run_cli("edit", "99", "Nope")
    assert invalid_edit.returncode != 0
    assert "invalid task" in (invalid_edit.stdout + invalid_edit.stderr).lower()

    todos = json.loads(DB_FILE.read_text(encoding="utf-8"))
    assert len(todos) == 2
    assert todos[0]["task"] == "Updated task text"
    assert todos[0]["due"] == "2026-05-20"
    assert todos[1]["task"] == "Fix bug"
    assert todos[1]["priority"] == "high"


def test_m4_existing_commands_and_readme_examples():
    """Verify existing behavior remains intact and README documents all commands."""
    assert README_FILE.exists()
    readme = README_FILE.read_text(encoding="utf-8").lower()
    for term in ["add", "list", "done", "clear-completed", "delete", "edit"]:
        assert term in readme

    run_cli("add", "Alpha")
    run_cli("add", "Beta", "--priority", "low")
    done = run_cli("done", "0")
    assert done.returncode == 0, done.stderr + done.stdout
    cleared = run_cli("clear-completed")
    assert cleared.returncode == 0, cleared.stderr + cleared.stdout

    listed = run_cli("list", "--json")
    assert listed.returncode == 0, listed.stderr + listed.stdout
    payload = json.loads(listed.stdout)
    assert len(payload) == 1
    assert payload[0]["task"] == "Beta"
    assert payload[0]["priority"] == "low"
