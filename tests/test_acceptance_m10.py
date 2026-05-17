"""Acceptance tests for M10.

These tests are generated before implementation and must fail initially (red phase).
After implementation, they must pass (green phase).
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB_FILE = REPO / "todos.json"
EXPORT_FILE = REPO / "tasks_export.json"
BACKUP_FILE = REPO / "backup.json"
README_FILE = REPO / "README.md"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "src.main", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
    )


def setup_function():
    for path in [DB_FILE, EXPORT_FILE, BACKUP_FILE]:
        if path.exists():
            path.unlink()


def teardown_function():
    for path in [DB_FILE, EXPORT_FILE, BACKUP_FILE]:
        if path.exists():
            path.unlink()


def test_m10_export_import_backup_restore_and_validation():
    """Verify export, import merge, import --replace, backup, restore, and invalid import data handling that must not mutate current task data."""
    add_first = run_cli("add", "Prepare invoice", "--due", "2026-05-20", "--priority", "high", "--repeat", "weekly", "--tag", "finance", "--tag", "urgent")
    assert add_first.returncode == 0, add_first.stderr + add_first.stdout
    add_second = run_cli("add", "Legacy friendly task")
    assert add_second.returncode == 0, add_second.stderr + add_second.stdout
    done_second = run_cli("done", "1")
    assert done_second.returncode == 0, done_second.stderr + done_second.stdout

    exported = run_cli("export", "tasks_export.json")
    assert exported.returncode == 0, exported.stderr + exported.stdout
    assert EXPORT_FILE.exists()
    exported_payload = json.loads(EXPORT_FILE.read_text(encoding="utf-8"))
    assert [item["task"] for item in exported_payload][:2] == ["Prepare invoice", "Legacy friendly task"]
    assert exported_payload[0]["priority"] == "high"
    assert exported_payload[0]["repeat"] == "weekly"
    assert exported_payload[0]["tags"] == ["finance", "urgent"]
    assert exported_payload[0]["due"] == "2026-05-20"
    assert exported_payload[1]["done"] is True

    DB_FILE.write_text(
        json.dumps([
            {"task": "Existing merge task", "done": False, "priority": "low"},
        ]),
        encoding="utf-8",
    )
    imported_merge = run_cli("import", "tasks_export.json")
    assert imported_merge.returncode == 0, imported_merge.stderr + imported_merge.stdout
    merged_payload = json.loads(DB_FILE.read_text(encoding="utf-8"))
    assert [item["task"] for item in merged_payload] == [
        "Existing merge task",
        "Prepare invoice",
        "Legacy friendly task",
    ]

    DB_FILE.write_text(json.dumps([{"task": "Replace me", "done": False}]), encoding="utf-8")
    imported_replace = run_cli("import", "tasks_export.json", "--replace")
    assert imported_replace.returncode == 0, imported_replace.stderr + imported_replace.stdout
    replaced_payload = json.loads(DB_FILE.read_text(encoding="utf-8"))
    assert [item["task"] for item in replaced_payload] == ["Prepare invoice", "Legacy friendly task"]

    backup_result = run_cli("backup", "backup.json")
    assert backup_result.returncode == 0, backup_result.stderr + backup_result.stdout
    assert BACKUP_FILE.exists()
    backup_payload = json.loads(BACKUP_FILE.read_text(encoding="utf-8"))
    assert backup_payload == replaced_payload

    DB_FILE.write_text(json.dumps([{"task": "Mutated task", "done": False}]), encoding="utf-8")
    restore_result = run_cli("restore", "backup.json")
    assert restore_result.returncode == 0, restore_result.stderr + restore_result.stdout
    restored_payload = json.loads(DB_FILE.read_text(encoding="utf-8"))
    assert restored_payload == backup_payload

    before_invalid = DB_FILE.read_text(encoding="utf-8")

    malformed = REPO / "bad_malformed.json"
    malformed.write_text("{not valid json", encoding="utf-8")
    malformed_result = run_cli("import", str(malformed.name))
    assert malformed_result.returncode != 0
    assert "malformed json" in (malformed_result.stdout + malformed_result.stderr).lower() or "json" in (malformed_result.stdout + malformed_result.stderr).lower()
    assert DB_FILE.read_text(encoding="utf-8") == before_invalid

    invalid_task = REPO / "bad_invalid_task.json"
    invalid_task.write_text(json.dumps([{"done": False}]), encoding="utf-8")
    invalid_task_result = run_cli("import", str(invalid_task.name))
    assert invalid_task_result.returncode != 0
    assert "invalid task record" in (invalid_task_result.stdout + invalid_task_result.stderr).lower() or "task" in (invalid_task_result.stdout + invalid_task_result.stderr).lower()
    assert DB_FILE.read_text(encoding="utf-8") == before_invalid

    invalid_priority = REPO / "bad_priority.json"
    invalid_priority.write_text(json.dumps([{"task": "Bad priority", "done": False, "priority": "urgent"}]), encoding="utf-8")
    invalid_priority_result = run_cli("restore", str(invalid_priority.name))
    assert invalid_priority_result.returncode != 0
    assert "invalid priority" in (invalid_priority_result.stdout + invalid_priority_result.stderr).lower() or "priority" in (invalid_priority_result.stdout + invalid_priority_result.stderr).lower()
    assert DB_FILE.read_text(encoding="utf-8") == before_invalid

    invalid_recurrence = REPO / "bad_recurrence.json"
    invalid_recurrence.write_text(json.dumps([{"task": "Bad recurrence", "done": False, "repeat": "yearly"}]), encoding="utf-8")
    invalid_recurrence_result = run_cli("restore", str(invalid_recurrence.name))
    assert invalid_recurrence_result.returncode != 0
    assert "invalid recurrence" in (invalid_recurrence_result.stdout + invalid_recurrence_result.stderr).lower() or "recurrence" in (invalid_recurrence_result.stdout + invalid_recurrence_result.stderr).lower()
    assert DB_FILE.read_text(encoding="utf-8") == before_invalid

    invalid_due = REPO / "bad_due.json"
    invalid_due.write_text(json.dumps([{"task": "Bad due", "done": False, "due": "2026/05/20"}]), encoding="utf-8")
    invalid_due_result = run_cli("import", str(invalid_due.name))
    assert invalid_due_result.returncode != 0
    assert "invalid due_date" in (invalid_due_result.stdout + invalid_due_result.stderr).lower() or "due" in (invalid_due_result.stdout + invalid_due_result.stderr).lower()
    assert DB_FILE.read_text(encoding="utf-8") == before_invalid

    invalid_tags = REPO / "bad_tags.json"
    invalid_tags.write_text(json.dumps([{"task": "Bad tags", "done": False, "tags": "finance"}]), encoding="utf-8")
    invalid_tags_result = run_cli("restore", str(invalid_tags.name))
    assert invalid_tags_result.returncode != 0
    assert "invalid tags shape" in (invalid_tags_result.stdout + invalid_tags_result.stderr).lower() or "tags" in (invalid_tags_result.stdout + invalid_tags_result.stderr).lower()
    assert DB_FILE.read_text(encoding="utf-8") == before_invalid

    invalid_text = REPO / "bad_text.json"
    invalid_text.write_text(json.dumps([{"task": "", "done": False}]), encoding="utf-8")
    invalid_text_result = run_cli("import", str(invalid_text.name))
    assert invalid_text_result.returncode != 0
    assert "invalid text" in (invalid_text_result.stdout + invalid_text_result.stderr).lower() or "text" in (invalid_text_result.stdout + invalid_text_result.stderr).lower()
    assert DB_FILE.read_text(encoding="utf-8") == before_invalid

    for path in [malformed, invalid_task, invalid_priority, invalid_recurrence, invalid_due, invalid_tags, invalid_text]:
        if path.exists():
            path.unlink()


def test_m10_backward_compatibility_regressions_and_readme():
    """Verify old-format JSON imports safely, existing features still work, and README documents export/import/backup/restore behavior."""
    legacy_payload = [
        {"task": "Legacy task", "done": False},
        {"task": "Recurring legacy", "done": False, "repeat": "monthly", "due": "2026-01-31", "priority": "medium"},
    ]
    EXPORT_FILE.write_text(json.dumps(legacy_payload), encoding="utf-8")

    imported_legacy = run_cli("import", "tasks_export.json", "--replace")
    assert imported_legacy.returncode == 0, imported_legacy.stderr + imported_legacy.stdout

    listed = run_cli("list", "--json")
    assert listed.returncode == 0, listed.stderr + listed.stdout
    payload = json.loads(listed.stdout)
    assert payload[0]["task"] == "Legacy task"
    assert payload[0].get("tags", []) == []
    assert payload[1]["repeat"] == "monthly"

    done_recurring = run_cli("done", "1")
    assert done_recurring.returncode == 0, done_recurring.stderr + done_recurring.stdout
    after_done = json.loads(DB_FILE.read_text(encoding="utf-8"))
    replacement = next(item for item in after_done if item["task"] == "Recurring legacy" and item.get("done") is False)
    assert replacement["due"] == "2026-02-28"
    assert replacement["priority"] == "medium"

    search_legacy = run_cli("list", "--search", "legacy")
    assert search_legacy.returncode == 0, search_legacy.stderr + search_legacy.stdout
    assert "Legacy task" in search_legacy.stdout

    delete_legacy = run_cli("delete", "0")
    assert delete_legacy.returncode == 0, delete_legacy.stderr + delete_legacy.stdout
    add_tagged = run_cli("add", "Tagged backup candidate", "--tag", "ops")
    assert add_tagged.returncode == 0, add_tagged.stderr + add_tagged.stdout
    backup_result = run_cli("backup", "backup.json")
    assert backup_result.returncode == 0, backup_result.stderr + backup_result.stdout
    assert BACKUP_FILE.exists()

    assert README_FILE.exists()
    readme = README_FILE.read_text(encoding="utf-8").lower()
    for term in [
        "export",
        "import merge",
        "import --replace",
        "backup",
        "restore",
        "invalid import",
        "backward compatibility",
        "readme",
    ]:
        assert term in readme
