"""Acceptance tests for M9: empty command.

Red phase: these tests MUST FAIL before implementation.

Coverage:
- empty command exists and exits 0
- empty reports zero items when store is empty
- empty reports non-zero items when store has items
- README documents empty
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


def reset_data():
    """Clear store for empty testing."""
    todos_file = REPO / "todos.json"
    if todos_file.exists():
        todos_file.unlink()


# ---------------------------------------------------------------------------
# T1: empty command exists and exits 0
# ---------------------------------------------------------------------------

def test_empty_command_exists():
    reset_data()
    result = run("empty")
    assert result.returncode == 0, (
        f"empty command must exit 0; got {result.returncode}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# T2: empty reports zero items when store is empty
# ---------------------------------------------------------------------------

def test_empty_reports_zero_items():
    reset_data()
    result = run("empty")
    assert result.returncode == 0
    lower = result.stdout.lower()
    assert "zero" in lower or "0" in result.stdout or "no items" in lower or "empty" in lower, (
        f"Expected message about zero/empty items; got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# T3: empty reports non-zero items when store has items
# ---------------------------------------------------------------------------

def test_empty_reports_non_zero_items():
    reset_data()
    run("add", "Task A")
    result = run("empty")
    assert result.returncode == 0
    lower = result.stdout.lower()
    assert "not empty" in lower or "1" in result.stdout or "has" in lower, (
        f"Expected message about non-zero items; got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# T4: README documents empty
# ---------------------------------------------------------------------------

def test_readme_contains_empty():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "empty" in readme.lower(), (
        "README.md must document the 'empty' command"
    )


# ---------------------------------------------------------------------------
# T5: prior features still work (backward compatibility)
# ---------------------------------------------------------------------------

def test_prior_add_and_list_still_work():
    reset_data()
    r_add = run("add", "backward compat check")
    assert r_add.returncode == 0, f"add broke: {r_add.stderr}"
    r_list = run("list")
    assert r_list.returncode == 0, f"list broke: {r_list.stderr}"
    assert "backward compat check" in r_list.stdout


def test_prior_done_and_clear_completed_still_work():
    reset_data()
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
