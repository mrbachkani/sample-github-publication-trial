"""Acceptance tests for M6: search command.

Red phase: these tests MUST FAIL before implementation.

Coverage:
- case-insensitive substring matching
- no match returns empty output, exits 0
- backward compatibility: prior commands still work
- readme documents search
"""
import subprocess
import sys
import json
from pathlib import Path

PYTHON = sys.executable
REPO = Path(__file__).resolve().parent.parent


def run(*args, input_text=None):
    result = subprocess.run(
        [PYTHON, "-m", "src.main"] + list(args),
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    return result


def setup_search_data():
    """Add known items for search testing."""
    # Clear first by removing todos.json
    todos_file = REPO / "todos.json"
    if todos_file.exists():
        todos_file.unlink()
    run("add", "Buy groceries at the store")
    run("add", "Write unit tests for search feature")
    run("add", "Fix the BUG in login module")
    run("add", "Deploy to production server")


# ---------------------------------------------------------------------------
# T1: search command exists and responds
# ---------------------------------------------------------------------------

def test_search_command_exists():
    setup_search_data()
    result = run("search", "groceries")
    assert result.returncode == 0, (
        f"search command must exit 0; got {result.returncode}\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# T2: case-insensitive matching — lowercase query matches mixed case item
# ---------------------------------------------------------------------------

def test_search_case_insensitive_lower_query():
    setup_search_data()
    result = run("search", "bug")
    assert result.returncode == 0
    assert "BUG" in result.stdout or "bug" in result.stdout.lower(), (
        f"Expected 'BUG' (case-insensitive) in output; got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# T3: case-insensitive matching — uppercase query matches lowercase item
# ---------------------------------------------------------------------------

def test_search_case_insensitive_upper_query():
    setup_search_data()
    result = run("search", "GROCERIES")
    assert result.returncode == 0
    assert "groceries" in result.stdout.lower(), (
        f"Expected 'groceries' match in output; got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# T4: substring matching — partial word finds correct items
# ---------------------------------------------------------------------------

def test_search_substring_match():
    setup_search_data()
    result = run("search", "unit")
    assert result.returncode == 0
    assert "unit tests" in result.stdout.lower() or "Write unit" in result.stdout, (
        f"Expected substring match for 'unit'; got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# T5: no match returns empty / no-match message, still exits 0
# ---------------------------------------------------------------------------

def test_search_no_match_exits_zero():
    setup_search_data()
    result = run("search", "xyzzy_not_found_abc")
    assert result.returncode == 0, (
        f"No-match search must still exit 0; got {result.returncode}\nstderr: {result.stderr}"
    )


def test_search_no_match_returns_no_items():
    setup_search_data()
    result = run("search", "xyzzy_not_found_abc")
    lower = result.stdout.lower()
    assert (
        "no" in lower
        or "0" in result.stdout
        or result.stdout.strip() == ""
        or "found" in lower
        or "match" in lower
    ), f"No-match output unclear; got:\n{result.stdout}"


# ---------------------------------------------------------------------------
# T6: README documents search
# ---------------------------------------------------------------------------

def test_readme_contains_search():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "search" in readme.lower(), (
        "README.md must document the 'search' command"
    )


# ---------------------------------------------------------------------------
# T7: prior features still work (backward compatibility)
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


def test_prior_count_still_works():
    todos_file = REPO / "todos.json"
    if todos_file.exists():
        todos_file.unlink()
    run("add", "item one")
    run("add", "item two")
    r = run("count")
    assert r.returncode == 0, f"count broke: {r.stderr}"
    assert "2" in r.stdout
