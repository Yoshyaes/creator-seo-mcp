from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> list[dict]:
    with open(FIXTURES_DIR / name) as f:
        return json.load(f)


def make_mock_service(rows: list[dict]) -> MagicMock:
    """Return a mock GSC service whose searchanalytics().query().execute() returns rows."""
    mock_service = MagicMock()
    mock_service.searchanalytics().query().execute.return_value = {"rows": rows}
    return mock_service


@pytest.fixture()
def mock_gsc_service(monkeypatch):
    """Fixture that patches get_service() to return a configurable mock."""
    mock = MagicMock()

    def _patch(module_path: str, rows: list[dict]):
        mock.searchanalytics().query().execute.return_value = {"rows": rows}
        monkeypatch.setattr(module_path, lambda: mock)
        return mock

    return _patch
