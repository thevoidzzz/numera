"""Run the model's statement, or refuse it, and return the executed number."""

from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from time import perf_counter
from typing import Literal

from numera.application.ports import AcceptsStatement, RunsStatement, StatementModel
from numera.domain.errors import ModelSchemaError, PrivilegeError, RequestError, StatementFailed
from numera.domain.limits import QUESTION_MAX_CHARS
from numera.domain.number import one_decimal


@dataclass(frozen=True, slots=True)
class Answer:
    """The executed statement and its number, or a refusal that still shows the SQL."""

    refused: bool
    reason: Literal["rejected_sql", "not_a_number"] | None
    sql: str
    value: Decimal | None
    model: str
    input_tokens: int
    output_tokens: int
    row_count: int
    model_ms: float
    execution_ms: float


def answer_question(
    question: str,
    model: StatementModel,
    accepts: AcceptsStatement,
    run: RunsStatement,
    *,
    clock: Callable[[], float] = perf_counter,
) -> Answer:
    """Ask the model for a statement. Execute it only when the gate accepts it.

    A schema mismatch is tried once more. A timeout is not retried.
    """

    if question.strip() == "":
        raise RequestError("question must not be empty")
    if len(question) > QUESTION_MAX_CHARS:
        raise RequestError(f"question must be at most {QUESTION_MAX_CHARS} characters")
    started = clock()
    proposed = _propose(model, question)
    model_ms = (clock() - started) * 1000
    if not accepts(proposed.sql):
        return _answer(
            proposed,
            refused=True,
            reason="rejected_sql",
            value=None,
            row_count=0,
            model_ms=model_ms,
            execution_ms=0.0,
        )
    started = clock()
    try:
        rows = run(proposed.sql)
    except PrivilegeError:
        execution_ms = (clock() - started) * 1000
        return _answer(proposed, refused=True, reason="rejected_sql", value=None, row_count=0, model_ms=model_ms, execution_ms=execution_ms)
    except StatementFailed:
        execution_ms = (clock() - started) * 1000
        return _answer(proposed, refused=True, reason="not_a_number", value=None, row_count=0, model_ms=model_ms, execution_ms=execution_ms)
    execution_ms = (clock() - started) * 1000
    ok, value = one_decimal(rows)
    if not ok:
        return _answer(
            proposed,
            refused=True,
            reason="not_a_number",
            value=None,
            row_count=len(rows),
            model_ms=model_ms,
            execution_ms=execution_ms,
        )
    return _answer(
        proposed,
        refused=False,
        reason=None,
        value=value,
        row_count=len(rows),
        model_ms=model_ms,
        execution_ms=execution_ms,
    )


def _propose(model: StatementModel, question: str):
    try:
        return model.propose(question)
    except ModelSchemaError:
        return model.propose(question)


def _answer(proposed, *, refused, reason, value, row_count, model_ms, execution_ms) -> Answer:
    return Answer(
        refused=refused,
        reason=reason,
        sql=proposed.sql,
        value=value,
        model=proposed.model,
        input_tokens=proposed.input_tokens,
        output_tokens=proposed.output_tokens,
        row_count=row_count,
        model_ms=model_ms,
        execution_ms=execution_ms,
    )
