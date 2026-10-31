"""POST /v1/answers. Refusals are 200. Transport and provider failures are problem+json."""

import logging

import pytest
from fastapi.testclient import TestClient

from numera.api import create_app
from numera.api.__main__ import app_from_env
from numera.domain.errors import DatabaseUnavailable, ModelSchemaError, ModelTimeout
from numera.domain.limits import QUESTION_MAX_CHARS
from numera.domain.model import ProposedStatement
from numera.infrastructure.reader import Reader
from numera.infrastructure.sql_gate import review_statement
from numera.infrastructure.stand_in import StandInModel
from numera.infrastructure.warehouse import load_warehouse

_SECRET = "sk-numera-test-key"
_PASSWORD = "warehouse-secret"


class ScriptedModel:
    """Returns one statement. The key and password must not reach the log."""

    def __init__(self, sql: str) -> None:
        self.calls = 0
        self.api_key = _SECRET
        self.password = _PASSWORD
        self.sql = sql

    def propose(self, question: str) -> ProposedStatement:
        self.calls += 1
        return ProposedStatement(sql=self.sql, model="scripted-model", input_tokens=3, output_tokens=4)


def _rows(rows: tuple[tuple[object, ...], ...]):
    def run(statement: str) -> tuple[tuple[object, ...], ...]:
        return rows

    return run


def test_executed_revenue_is_200_and_the_log_omits_secrets(
    database_url: str, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO, logger="numera.api")
    load_warehouse(database_url)
    model = StandInModel()
    model.api_key = _SECRET
    model.password = _PASSWORD
    client = TestClient(create_app(model, review_statement, Reader(database_url).run))

    response = client.post("/v1/answers", json={"question": "What is West desk revenue for March 2026?"})

    assert response.status_code == 200
    body = response.json()
    assert body["request_id"] == response.headers["X-Request-ID"]
    assert body["refused"] is False
    assert body["reason"] is None
    assert body["value"] == "1750.50"
    assert body["sql"].startswith("SELECT SUM(amount)")
    assert "model=sql-stand-in" in caplog.text
    assert "input_tokens=" in caplog.text
    assert "output_tokens=" in caplog.text
    assert "refused=false" in caplog.text
    assert "row_count=1" in caplog.text
    assert "model_ms=" in caplog.text
    assert "execution_ms=" in caplog.text
    assert "sql=SELECT SUM(amount)" in caplog.text
    assert "question=What is West desk revenue for March 2026?" in caplog.text
    assert _SECRET not in caplog.text
    assert _PASSWORD not in caplog.text
    assert _SECRET not in response.text
    assert database_url not in response.text
    assert database_url not in caplog.text


def test_a_forbidden_statement_is_200(database_url: str) -> None:
    load_warehouse(database_url)
    client = TestClient(create_app(StandInModel(), review_statement, Reader(database_url).run))

    response = client.post("/v1/answers", json={"question": "Drop the journal lines."})

    assert response.status_code == 200
    body = response.json()
    assert body["refused"] is True
    assert body["reason"] == "rejected_sql"
    assert body["value"] is None
    assert body["sql"] == "DROP TABLE warehouse.journal_line"


def test_a_result_that_is_not_one_number_is_200(database_url: str) -> None:
    load_warehouse(database_url)
    client = TestClient(
        create_app(ScriptedModel("SELECT memo FROM warehouse.journal_line WHERE line_id = 1"), review_statement, Reader(database_url).run)
    )

    response = client.post("/v1/answers", json={"question": "Show the memo."})

    assert response.status_code == 200
    assert response.json()["refused"] is True
    assert response.json()["reason"] == "not_a_number"
    assert response.json()["value"] is None


def test_a_null_cell_is_200_with_a_null_value() -> None:
    client = TestClient(create_app(ScriptedModel("SELECT NULL::numeric"), review_statement, _rows(((None,),))))

    response = client.post("/v1/answers", json={"question": "What is the missing amount?"})

    assert response.status_code == 200
    assert response.json()["refused"] is False
    assert response.json()["value"] is None


def test_invalid_input_is_400() -> None:
    model = ScriptedModel("SELECT 1")
    client = TestClient(create_app(model, review_statement, _rows(((1,),))))

    empty = client.post("/v1/answers", json={"question": "  "})
    missing = client.post("/v1/answers", json={})
    garbled = client.post("/v1/answers", content=b"not-json", headers={"content-type": "application/json"})
    oversized = client.post("/v1/answers", json={"question": "m" * (QUESTION_MAX_CHARS + 1)})

    assert empty.status_code == 400
    assert empty.json()["detail"] == "question must not be empty"
    assert missing.status_code == 400
    assert missing.json()["detail"] == "question is required"
    assert garbled.status_code == 400
    assert garbled.json()["detail"] == "request body must be json"
    assert oversized.status_code == 400
    assert str(QUESTION_MAX_CHARS) in oversized.json()["detail"]
    for response in (empty, missing, garbled, oversized):
        assert response.headers["content-type"].startswith("application/problem+json")
        assert response.json()["status"] == 400
        assert response.json()["request_id"] == response.headers["X-Request-ID"]
    assert model.calls == 0


def test_a_timeout_is_504_and_is_not_retried() -> None:
    class _Slow(ScriptedModel):
        def propose(self, question: str) -> ProposedStatement:
            self.calls += 1
            raise ModelTimeout("slow")

    model = _Slow("SELECT 1")
    client = TestClient(create_app(model, review_statement, _rows(((1,),))))

    response = client.post("/v1/answers", json={"question": "What is the total?"})

    assert response.status_code == 504
    assert response.json()["detail"] == "the model did not respond in time"
    assert response.headers["content-type"].startswith("application/problem+json")
    assert model.calls == 1


def test_a_schema_mismatch_is_retried_once_and_then_502() -> None:
    class _Once(ScriptedModel):
        def propose(self, question: str) -> ProposedStatement:
            self.calls += 1
            if self.calls == 1:
                raise ModelSchemaError("not a statement")
            return ProposedStatement(sql=self.sql, model="scripted-model", input_tokens=3, output_tokens=4)

    recovered = _Once("SELECT 1")
    client = TestClient(create_app(recovered, review_statement, _rows(((1,),))))
    ok = client.post("/v1/answers", json={"question": "What is the total?"})
    assert ok.status_code == 200
    assert ok.json()["value"] == "1"
    assert recovered.calls == 2

    class _Twice(ScriptedModel):
        def propose(self, question: str) -> ProposedStatement:
            self.calls += 1
            raise ModelSchemaError("not a statement")

    failed = _Twice("SELECT 1")
    client = TestClient(create_app(failed, review_statement, _rows(((1,),))))
    response = client.post("/v1/answers", json={"question": "What is the total?"})
    assert response.status_code == 502
    assert response.json()["detail"] == "the model response did not match the schema"
    assert response.headers["content-type"].startswith("application/problem+json")
    assert failed.calls == 2


def test_a_down_database_is_503_and_hides_the_connection_string() -> None:
    url = "postgresql://numera:warehouse-secret@127.0.0.1:1/numera"
    client = TestClient(create_app(ScriptedModel("SELECT 1"), review_statement, Reader(url).run))

    response = client.post("/v1/answers", json={"question": "What is the total?"})

    assert response.status_code == 503
    assert response.json()["detail"] == "the warehouse is unavailable"
    assert response.headers["content-type"].startswith("application/problem+json")
    assert "127.0.0.1" not in response.text
    assert "warehouse-secret" not in response.text
    assert url not in response.text


def test_database_unavailable_from_the_runner_is_503() -> None:
    def run(statement: str) -> tuple[tuple[object, ...], ...]:
        raise DatabaseUnavailable("the warehouse is unavailable")

    client = TestClient(create_app(ScriptedModel("SELECT 1"), review_statement, run))
    response = client.post("/v1/answers", json={"question": "What is the total?"})

    assert response.status_code == 503
    assert "postgresql" not in response.text


def test_the_process_requires_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(SystemExit, match="DATABASE_URL"):
        app_from_env()
