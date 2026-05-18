"""Acceptance tests for M14.

These tests are generated before implementation and must fail initially (red phase).
After implementation, they must pass (green phase).
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB_FILE = REPO / "todos.json"
IMPORT_FILE = REPO / "test_import.json"
README_FILE = REPO / "README.md"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "src.main", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
    )


def setup_function():
    for path in [DB_FILE, IMPORT_FILE]:
        if path.exists():
            path.unlink()


def teardown_function():
    for path in [DB_FILE, IMPORT_FILE]:
        if path.exists():
            path.unlink()


def test_m14_import_valid_json():
    """Verify import command can import valid JSON tasks."""
    IMPORT_FILE.write_text(json.dumps([
        {"task": "Imported task 1", "done": False},
        {"task": "Imported task 2", "done": True}
    ]), encoding="utf-8")
    result = run_cli("import", "test_import.json")
    assert result.returncode == 0, result.stderr + result.stdout
    
    list_result = run_cli("list")
    assert list_result.returncode == 0
    assert "Imported task 1" in list_result.stdout
    assert "Imported task 2" in list_result.stdout


def test_m14_import_missing_file():
    """Verify import fails clearly on missing file."""
    result = run_cli("import", "nonexistent.json")
    assert result.returncode != 0, "Import should fail on missing file"
    output = (result.stdout + result.stderr).lower()
    assert "not found" in output or "no such file" in output or "missing" in output


def test_m14_import_invalid_json():
    """Verify import fails clearly on invalid JSON (malformed JSON)."""
    IMPORT_FILE.write_text("{not valid json", encoding="utf-8")
    result = run_cli("import", "test_import.json")
    assert result.returncode != 0, "Import should fail on invalid JSON"
    output = (result.stdout + result.stderr).lower()
    assert "json" in output or "parse" in output or "invalid" in output or "malformed" in output


def test_m14_import_readme_documented():
    """Verify README documents import command."""
    assert README_FILE.exists()
    readme = README_FILE.read_text(encoding="utf-8").lower()
    assert "import" in readme


def test_m14_prior_commands_still_work():
    """Verify prior accepted commands still work after import."""
    add_result = run_cli("add", "Original task")
    assert add_result.returncode == 0
    
    list_result = run_cli("list")
    assert list_result.returncode == 0
    assert "Original task" in list_result.stdout
