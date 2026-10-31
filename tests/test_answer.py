"""The number in an answer is the one the reader executed."""

from decimal import Decimal

import psycopg
import pytest

from numera.application.answer import answer_question
from numera.domain.errors import DatabaseUnavailable, ModelSchemaError
from numera.domain.model import ProposedStatement
from numera.infrastructure.reader import Reader
from numera.infrastructure.sql_gate import review_statement
from numera.infrastructure.stand_in import MODEL_NAME, StandInModel
from numera.infrastructure.warehouse import load_warehouse

_WEST_MARCH = "What is West desk revenue for March 2026?"


class ScriptedModel:
    """Returns one fixed statement. The number is not part of the script."""

    def __init__(self, sql: str) -> None:
        self.sql = sql

    def propose(self, question: str) -> ProposedStatement:
        return ProposedStatement(sql=self.sql, model="scripted", input_tokens=1, output_tokens=1)


def _answer(database_url: str, sql: str):
    load_warehouse(database_url)
    return answer_question("What is the total?", ScriptedModel(sql), review_statement, Reader(database_url).run)


def test_stand_in_returns_the_executed_west_march_revenue(database_url: str) -> None:
    load_warehouse(database_url)
    model = StandInModel()
    proposed = model.propose(_WEST_MARCH)

    result = answer_question(_WEST_MARCH, model, review_statement, Reader(database_url).run)

    assert result.refused is False
    assert result.reason is None
    assert result.sql == proposed.sql
    assert result.value == Decimal("1750.50")
    assert result.model == MODEL_NAME
    assert result.row_count == 1


def test_scripted_select_uses_the_database_value_not_the_question(database_url: str) -> None:
    result = _answer(database_url, "SELECT 1")

    assert result.refused is False
    assert result.value == Decimal("1")
    assert result.sql == "SELECT 1"


def test_drop_is_refused_and_the_seed_stays(database_url: str) -> None:
    load_warehouse(database_url)
    result = answer_question("Drop the journal lines.", StandInModel(), review_statement, Reader(database_url).run)

    assert result.refused is True
    assert result.reason == "rejected_sql"
    assert result.value is None
    assert result.execution_ms == 0
    with psycopg.connect(database_url) as conn:
        count = conn.execute("SELECT COUNT(*) FROM warehouse.journal_line").fetchone()[0]
    assert count == 7


def test_rejected_sql_does_not_call_the_runner() -> None:
    def runner(statement: str) -> tuple[tuple[object, ...], ...]:
        raise AssertionError(statement)

    result = answer_question("Drop it.", ScriptedModel("DROP TABLE warehouse.journal_line"), review_statement, runner)

    assert result.reason == "rejected_sql"
    assert result.row_count == 0


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT line_id, amount FROM warehouse.journal_line WHERE line_id = 1",
        "SELECT amount FROM warehouse.journal_line WHERE entity_code = 'WEST' AND period_code = '2026-03'",
        "SELECT amount FROM warehouse.journal_line WHERE line_id = 0",
        "SELECT memo FROM warehouse.journal_line WHERE line_id = 1",
        "SELECT true",
        "SELECT 50::float8",
        "SELECT missing FROM warehouse.journal_line",
    ],
)
def test_a_result_that_is_not_one_number_is_refused(database_url: str, sql: str) -> None:
    result = _answer(database_url, sql)

    assert result.refused is True
    assert result.reason == "not_a_number"
    assert result.value is None
    assert result.sql == sql


def test_null_cell_is_an_executed_value(database_url: str) -> None:
    result = _answer(database_url, "SELECT NULL::numeric")

    assert result.refused is False
    assert result.value is None
    assert result.row_count == 1


def test_reader_privilege_failure_is_refused_without_the_owner(database_url: str) -> None:
    result = _answer(database_url, "SELECT rolpassword FROM pg_authid")

    assert result.refused is True
    assert result.reason == "rejected_sql"
    assert result.value is None


def test_down_database_omits_the_connection_string() -> None:
    with pytest.raises(DatabaseUnavailable) as caught:
        answer_question(
            "What is the total?",
            ScriptedModel("SELECT 1"),
            review_statement,
            Reader("postgresql://numera@127.0.0.1:1/numera").run,
        )

    message = str(caught.value)
    assert "numera" not in message
    assert "127.0.0.1" not in message


def test_stand_in_does_not_invent_a_statement() -> None:
    with pytest.raises(ModelSchemaError):
        StandInModel().propose("What is the meaning of the accrual?")
