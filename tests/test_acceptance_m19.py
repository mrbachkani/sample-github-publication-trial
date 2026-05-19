"""Acceptance tests for M19.

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


def test_m19_task_summary_json_command():
    """Verify `task-summary-json` returns the correct count of stored items."""
    # Empty list should return 0
    empty = run_cli("task-summary-json")
    assert empty.returncode == 0, empty.stderr + empty.stdout
    assert "0" in empty.stdout or "no items" in empty.stdout.lower() or "empty" in empty.stdout.lower()

    # After adding items, count should match
    run_cli("add", "First task")
    run_cli("add", "Second task")
    result = run_cli("task-summary-json")
    assert result.returncode == 0, result.stderr + result.stdout
    assert "2" in result.stdout


def test_m19_task_summary_json_readme_documented():
    """Verify README documents `task-summary-json`."""
    assert README_FILE.exists()
    readme = README_FILE.read_text(encoding="utf-8").lower()
    assert "task-summary-json" in readme
