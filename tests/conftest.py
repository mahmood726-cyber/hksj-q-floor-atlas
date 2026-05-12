"""Shared pytest fixtures for hksj-q-floor-atlas tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture(scope="session")
def golden_mas() -> list[dict]:
    """3 hand-verified MAs with metafor-reference expected values."""
    path = FIXTURES_DIR / "golden_mas.json"
    if not path.exists():
        pytest.skip("golden_mas.json not yet generated (Task 8)")
    return json.loads(path.read_text())
