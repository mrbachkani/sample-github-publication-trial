"""Acceptance tests for M1.

These tests are generated before implementation and must fail initially (red phase).
After implementation, they must pass (green phase).
"""

import subprocess
import sys


def test_m1_cli_contract():
    result = subprocess.run(
        [sys.executable, "-m", "src.main", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
