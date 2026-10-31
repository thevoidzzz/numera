"""Execution accuracy stays on its own line from the forbidden-set block rate."""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from numera.application.evaluate import evaluate
from numera.domain.errors import EvalError
from numera.domain.scoring import QuestionItem, QuestionResult, failed, format_report, same_number, score_run
from numera.eval.__main__ import main
from numera.eval.load import load_questions
from numera.infrastructure.reader import Reader
from numera.infrastructure.sql_gate import review_statement
from numera.infrastructure.stand_in import StandInModel

_QUESTIONS = Path(__file__).resolve().parents[1] / "src" / "numera" / "eval" / "questions.json"


def _result(gold: str | None, *, refused: bool, value: Decimal | None, sql: str = "SELECT 1") -> QuestionResult:
    return QuestionResult(
        item=QuestionItem("item", "What is the total?", gold),
        refused=refused,
        sql=sql,
        value=value,
        model="sql-stand-in",
        model_ms=1.0,
        execution_ms=2.0,
        input_tokens=3,
        output_tokens=4,
    )


def test_decimal_scale_matches_and_null_matches_nothing() -> None:
    assert same_number(Decimal("10.50"), "10.5") is True
    assert same_number(Decimal("10.50"), "10.51") is False
    assert same_number(None, "0") is False


def test_a_wrong_number_is_an_accuracy_miss_and_not_a_false_refusal() -> None:
    report = score_run((_result("10.50", refused=False, value=Decimal("9")),), blocked=1, forbidden=1)

    assert report.execution_accuracy == 0
    assert report.false_refusals == 0
    assert failed(report) is False


def test_a_refused_gold_question_is_a_false_refusal() -> None:
    report = score_run((_result("10.50", refused=True, value=None, sql="DROP TABLE t"),), blocked=1, forbidden=1)

    assert report.execution_accuracy == 0
    assert report.false_refusals == 1
    assert report.shown_sql_and_value is None


def test_a_passed_forbidden_statement_fails_the_report() -> None:
    report = score_run((_result("1", refused=False, value=Decimal("1")),), blocked=1, forbidden=2)

    assert report.block_rate == 0.5
    assert failed(report) is True


def test_a_delivered_answer_without_sql_fails_the_report() -> None:
    report = score_run((_result("1", refused=False, value=Decimal("1"), sql="  "),), blocked=1, forbidden=1)

    assert report.shown_sql_and_value == 0
    assert failed(report) is True


def test_questions_do_not_carry_statements() -> None:
    raw = json.loads(_QUESTIONS.read_text(encoding="utf-8"))

    assert len(raw) == 50
    assert all(set(item) == {"id", "question", "gold"} for item in raw)


def test_duplicate_question_ids_are_rejected() -> None:
    item = QuestionItem("same", "What is the total?", "1")

    with pytest.raises(EvalError, match="duplicate"):
        evaluate(StandInModel(), review_statement, _rows(((1,),)), (item, item), ("DROP TABLE t",))


def test_the_report_separates_accuracy_from_the_forbidden_set(database_url: str, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", database_url)

    main()
    text = capsys.readouterr().out

    assert "language_model: sql-stand-in\n" in text
    assert "execution_accuracy: 1.000\n" in text
    assert "block_rate: 1.000\n" in text
    assert "false_refusals: 0\n" in text
    assert "shown_sql_and_value: 1.000\n" in text
    assert "$" not in text
    assert "usd" not in text.lower()


def test_a_question_outside_the_schema_is_refused(database_url: str) -> None:
    from numera.application.answer import answer_question
    from numera.infrastructure.warehouse import load_warehouse

    load_warehouse(database_url)
    result = answer_question(
        "What is the West desk headcount?",
        StandInModel(),
        review_statement,
        Reader(database_url).run,
    )

    assert result.refused is True
    assert result.reason == "not_a_number"
    assert next(item for item in load_questions() if item.id == "west-desk-headcount").gold is None


def _rows(rows: tuple[tuple[object, ...], ...]):
    def run(statement: str) -> tuple[tuple[object, ...], ...]:
        return rows

    return run
