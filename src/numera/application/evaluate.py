"""Run the fixed question set. This module does not open a driver."""

from collections.abc import Sequence
from decimal import Decimal, InvalidOperation

from numera.application.answer import answer_question
from numera.application.ports import AcceptsStatement, RunsStatement, StatementModel
from numera.domain.errors import EvalError, ModelSchemaError
from numera.domain.scoring import QuestionItem, QuestionResult, EvalReport, score_run


def evaluate(
    model: StatementModel,
    accepts: AcceptsStatement,
    run: RunsStatement,
    items: Sequence[QuestionItem],
    forbidden: Sequence[str],
) -> EvalReport:
    """Execute every question and score the forbidden statements without running them."""

    if not items:
        raise EvalError("the evaluation set is empty")
    if not forbidden:
        raise EvalError("the forbidden set is empty")
    _reject_bad_items(items)
    results: list[QuestionResult] = []
    for item in items:
        try:
            answer = answer_question(item.question, model, accepts, run)
        except ModelSchemaError as exc:
            raise EvalError(f"no statement for {item.id}") from exc
        results.append(
            QuestionResult(
                item=item,
                refused=answer.refused,
                sql=answer.sql,
                value=answer.value,
                model=answer.model,
                model_ms=answer.model_ms,
                execution_ms=answer.execution_ms,
                input_tokens=answer.input_tokens,
                output_tokens=answer.output_tokens,
            )
        )
    blocked = sum(1 for statement in forbidden if not accepts(statement))
    try:
        return score_run(results, blocked, len(forbidden))
    except ValueError as exc:
        raise EvalError(str(exc)) from exc


def _reject_bad_items(items: Sequence[QuestionItem]) -> None:
    seen: set[str] = set()
    for item in items:
        if item.id in seen:
            raise EvalError(f"duplicate question id: {item.id}")
        seen.add(item.id)
        if item.question.strip() == "":
            raise EvalError(f"question must not be empty: {item.id}")
        if item.gold is None:
            continue
        try:
            Decimal(item.gold)
        except InvalidOperation as exc:
            raise EvalError(f"gold must be a decimal: {item.id}") from exc
