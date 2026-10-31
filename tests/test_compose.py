"""The image runs the same suite. PostgreSQL stays on the Compose network."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from numera.api.__main__ import app_from_env

_COMPOSE = Path("compose.yaml")


def test_compose_publishes_the_api_and_keeps_the_database_private() -> None:
    text = _COMPOSE.read_text(encoding="utf-8")

    assert text.count("\n    ports:") == 1
    assert '"8000:8000"' in text
    assert "5432:5432" not in text


def test_the_process_loads_the_seed(database_url: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", database_url)
    client = TestClient(app_from_env())

    response = client.post("/v1/answers", json={"question": "What is West desk revenue for March 2026?"})

    assert response.status_code == 200
    assert response.json()["value"] == "1750.50"
