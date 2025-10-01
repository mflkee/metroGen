from __future__ import annotations

import subprocess
import sys


def test_ruff_clean() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
