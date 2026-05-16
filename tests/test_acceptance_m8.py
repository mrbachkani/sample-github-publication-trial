"""Acceptance tests for M8: clear command.

Red phase: these tests MUST FAIL before implementation.

Coverage:
- clear command exists and exits 0
- clear removes all stored items
- clear returns a clear success message
- README documents clear
- backward compatibility: prior commands still work
"""
import subprocess
import sys
import json
from pathlib import Path

PYTHON = sys.executable
REPO = Path(__file__).resolve().parent.parent


def run(*args):
    result = subprocess.run(
        [PYTHON, "-m", "src.main"] + list(args),
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    return result


def setup_data():
    """Add known items for clear testing."""
    todos_file = REPO / "todos.json"
    if todos_file.exists():
        todos_file.unlink()
    run("add", "Task A")
    run("add", "Task B", "--priority", "high")
    run("add", "Task C", "--due", "2026-12-31")


# ---------------------------------------------------------------------------
# T1: clear command exists and exits 0
# ---------------------------------------------------------------------------

def test_clear_command_exists():
    setup_data()
    result = run("clear")
    assert result.returncode == 0, (
        f"clear command must exit 0; got {result.returncode}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# T2: clear removes all stored items
# ---------------------------------------------------------------------------

def test_clear_removes_all_items():
    setup_data()
    result = run("clear")
    assert result.returncode == 0
    listed = run("list")
    assert listed.returncode == 0
    assert "Task A" not in listed.stdout
    assert "Task B" not in listed.stdout
    assert "Task C" not in listed.stdout
    # After clear, list should report empty
    lower = listed.stdout.lower()
    assert "no tasks" in lower or "0" in listed.stdout or listed.stdout.strip() == "", (
        f"Expected empty list after clear; got:\n{listed.stdout}"
    )


# ---------------------------------------------------------------------------
# T3: clear returns a clear success message
# ---------------------------------------------------------------------------

def test_clear_returns_success_message():
    setup_data()
    result = run("clear")
    assert result.returncode == 0
    lower = result.stdout.lower()
    assert "clear" in lower or "removed" in lower or "deleted" in lower or "emptied" in lower, (
        f"Expected success message containing 'clear' or similar; got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# T4: README documents clear
# ---------------------------------------------------------------------------

def test_readme_contains_clear():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "clear" in readme.lower(), (
        "README.md must document the 'clear' command"
    )


# ---------------------------------------------------------------------------
# T5: prior features still work (backward compatibility)
# ---------------------------------------------------------------------------

def test_prior_add_and_list_still_work():
    todos_file = REPO / "todos.json"
    if todos_file.exists():
        todos_file.unlink()
    r_add = run("add", "backward compat check")
    assert r_add.returncode == 0, f"add broke: {r_add.stderr}"
    r_list = run("list")
    assert r_list.returncode == 0, f"list broke: {r_list.stderr}"
    assert "backward compat check" in r_list.stdout


def test_prior_done_and_clear_completed_still_work():
    todos_file = REPO / "todos.json"
    if todos_file.exists():
        todos_file.unlink()
    run("add", "item one")
    run("add", "item two")
    r_done = run("done", "0")
    assert r_done.returncode == 0, f"done broke: {r_done.stderr}"
    r_clear_completed = run("clear-completed")
    assert r_clear_completed.returncode == 0, (
        f"clear-completed broke: {r_clear_completed.stderr}"
    )
    listed = run("list")
    assert listed.returncode == 0
    assert "item two" in listed.stdout
    assert "item one" not in listed.stdout
