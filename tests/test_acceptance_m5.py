"""Acceptance tests for M5.

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


def test_m5_list_filters_sorting_json_and_backward_compatibility():
    """Verify --status, --priority, --due-before, --sort, --json, invalid status/sort/date, and backward compatibility."""
    DB_FILE.write_text(
        json.dumps([
            {"task": "Legacy pending", "done": False},
            {"task": "High urgent", "done": False, "priority": "high", "due": "2026-05-10"},
            {"task": "Medium later", "done": False, "priority": "medium", "due": "2026-06-02"},
            {"task": "Low completed", "done": True, "priority": "low", "due": "2026-05-08"},
            {"task": "No due high", "done": False, "priority": "high"},
            {"task": "Due only pending", "done": False, "due": "2026-05-31"}
        ]),
        encoding="utf-8",
    )

    pending = run_cli("list", "--status", "pending")
    assert pending.returncode == 0, pending.stderr + pending.stdout
    assert "High urgent" in pending.stdout
    assert "Low completed" not in pending.stdout

    completed = run_cli("list", "--status", "completed")
    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert "Low completed" in completed.stdout
    assert "High urgent" not in completed.stdout

    high_only = run_cli("list", "--priority", "high")
    assert high_only.returncode == 0, high_only.stderr + high_only.stdout
    assert "High urgent" in high_only.stdout
    assert "No due high" in high_only.stdout
    assert "Medium later" not in high_only.stdout

    medium_only = run_cli("list", "--priority", "medium")
    assert medium_only.returncode == 0, medium_only.stderr + medium_only.stdout
    assert "Medium later" in medium_only.stdout
    assert "High urgent" not in medium_only.stdout

    low_only = run_cli("list", "--priority", "low")
    assert low_only.returncode == 0, low_only.stderr + low_only.stdout
    assert "Low completed" in low_only.stdout
    assert "Medium later" not in low_only.stdout

    due_before = run_cli("list", "--due-before", "2026-05-31")
    assert due_before.returncode == 0, due_before.stderr + due_before.stdout
    assert "High urgent" in due_before.stdout
    assert "Due only pending" in due_before.stdout
    assert "Medium later" not in due_before.stdout
    assert "No due high" not in due_before.stdout

    combined = run_cli("list", "--status", "pending", "--priority", "high", "--due-before", "2026-05-31", "--sort", "due")
    assert combined.returncode == 0, combined.stderr + combined.stdout
    lines = [line for line in combined.stdout.splitlines() if line.strip()]
    assert any("High urgent" in line for line in lines)
    assert all("No due high" not in line for line in lines)
    assert all("Low completed" not in line for line in lines)

    sorted_due = run_cli("list", "--sort", "due", "--json")
    assert sorted_due.returncode == 0, sorted_due.stderr + sorted_due.stdout
    due_payload = json.loads(sorted_due.stdout)
    due_tasks = [item["task"] for item in due_payload]
    assert due_tasks[:4] == ["Low completed", "High urgent", "Due only pending", "Medium later"]
    assert due_tasks[-2:] == ["Legacy pending", "No due high"]

    sorted_priority = run_cli("list", "--sort", "priority", "--json")
    assert sorted_priority.returncode == 0, sorted_priority.stderr + sorted_priority.stdout
    priority_payload = json.loads(sorted_priority.stdout)
    priority_tasks = [item["task"] for item in priority_payload]
    high_positions = [priority_tasks.index("High urgent"), priority_tasks.index("No due high")]
    medium_position = priority_tasks.index("Medium later")
    low_position = priority_tasks.index("Low completed")
    legacy_position = priority_tasks.index("Legacy pending")
    due_only_position = priority_tasks.index("Due only pending")
    assert max(high_positions) < medium_position < low_position
    assert low_position < legacy_position
    assert legacy_position < due_only_position

    sorted_id = run_cli("list", "--sort", "id", "--json")
    assert sorted_id.returncode == 0, sorted_id.stderr + sorted_id.stdout
    id_payload = json.loads(sorted_id.stdout)
    assert [item["task"] for item in id_payload] == [
        "Legacy pending",
        "High urgent",
        "Medium later",
        "Low completed",
        "No due high",
        "Due only pending",
    ]

    filtered_json = run_cli("list", "--priority", "high", "--sort", "due", "--json")
    assert filtered_json.returncode == 0, filtered_json.stderr + filtered_json.stdout
    filtered_payload = json.loads(filtered_json.stdout)
    assert [item["task"] for item in filtered_payload] == ["High urgent", "No due high"]

    invalid_status = run_cli("list", "--status", "stuck")
    assert invalid_status.returncode != 0
    assert "invalid status" in (invalid_status.stdout + invalid_status.stderr).lower()

    invalid_priority = run_cli("list", "--priority", "urgent")
    assert invalid_priority.returncode != 0
    invalid_priority_output = (invalid_priority.stdout + invalid_priority.stderr).lower()
    assert "priority" in invalid_priority_output
    assert "high" in invalid_priority_output

    invalid_sort = run_cli("list", "--sort", "deadline")
    assert invalid_sort.returncode != 0
    assert "invalid sort" in (invalid_sort.stdout + invalid_sort.stderr).lower()

    invalid_date = run_cli("list", "--due-before", "2026/05/31")
    assert invalid_date.returncode != 0
    assert "invalid date" in (invalid_date.stdout + invalid_date.stderr).lower()


def test_m5_existing_commands_and_readme_examples():
    """Verify regressions do not break existing commands and README examples are present."""
    assert README_FILE.exists()
    readme = README_FILE.read_text(encoding="utf-8").lower()
    for term in [
        "--status",
        "--priority",
        "--due-before",
        "--sort",
        "--json",
        "pending",
        "completed",
        "combined",
    ]:
        assert term in readme

    add_due = run_cli("add", "Pay electricity bill", "--due", "2026-05-20")
    assert add_due.returncode == 0, add_due.stderr + add_due.stdout
    add_priority = run_cli("add", "Fix bug", "--priority", "high")
    assert add_priority.returncode == 0, add_priority.stderr + add_priority.stdout
    done = run_cli("done", "0")
    assert done.returncode == 0, done.stderr + done.stdout
    edit = run_cli("edit", "1", "Fix critical bug")
    assert edit.returncode == 0, edit.stderr + edit.stdout
    delete = run_cli("delete", "0")
    assert delete.returncode == 0, delete.stderr + delete.stdout

    listed = run_cli("list", "--status", "pending", "--json")
    assert listed.returncode == 0, listed.stderr + listed.stdout
    payload = json.loads(listed.stdout)
    assert len(payload) == 1
    assert payload[0]["task"] == "Fix critical bug"
    assert payload[0]["priority"] == "high"

    clear = run_cli("clear-completed")
    assert clear.returncode == 0, clear.stderr + clear.stdout
