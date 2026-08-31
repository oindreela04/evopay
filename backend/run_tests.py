"""Run the canonical isolated backend test suite.

Authentication and ownership tests require independent temporary databases, so
the maintained pytest suite is the single source of truth for backend checks.
"""

from pathlib import Path

import pytest


if __name__ == "__main__":
    raise SystemExit(pytest.main(["-q", str(Path(__file__).parent / "tests")]))
