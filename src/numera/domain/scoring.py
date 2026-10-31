"""Score executed numbers apart from blocked statements."""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class QuestionItem:
    """One hand-written question. Gold is a decimal string, or none when no number exists."""

    id: str
    question: str
    gold: str | None


@dataclass(frozen=True, slots=True)
class QuestionResult:
    """What the answer contract did with one item."""

    item: QuestionItem
    refused: bool
    sql: str
    value: Decimal | None
    model: str
    model_ms: float
    execution_ms: float
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True, slots=True)
class EvalReport:
    """Printed baseline. Accuracy is none when no question has a gold number."""

    language_model: str
    questions: int
    scored_questions: int
    execution_accuracy: float | None
    block_rate: float
    shown_sql_and_value: float | None
    false_refusals: int
    model_ms_p95: float
    execution_ms_p95: float
    input_tokens: int
    output_tokens: int


def same_number(value: Decimal | None, gold: str) -> bool:
    """Decimal equality. Scale does not matter, and NULL matches nothing."""

    if value is None:
        return False
    return value == Decimal(gold)


def percentile(values: Sequence[float], percent: float) -> float:
    """Nearest-rank percentile. `percent` is in (0, 100]."""

    if not values:
        raise ValueError("percentile needs at least one value")
    if not 0 < percent <= 100:
        raise ValueError("percent must be in (0, 100]")
    ordered = sorted(values)
    rank = math.ceil(percent / 100 * len(ordered))
    return ordered[rank - 1]


def score_run(results: Sequence[QuestionResult], blocked: int, forbidden: int) -> EvalReport:
    """Accuracy uses only questions with a gold number. The forbidden set is separate."""

    if not results:
        raise ValueError("the evaluation set is empty")
    if forbidden < 1:
        raise ValueError("the forbidden set is empty")
    scored = [result for result in results if result.item.gold is not None]
    correct = sum(1 for result in scored if _correct(result))
    shown = [result for result in results if not result.refused]
    if not shown:
        shown_rate = None
    else:
        complete = sum(1 for result in shown if result.sql.strip() != "")
        shown_rate = complete / len(shown)
    return EvalReport(
        language_model=results[0].model,
        questions=len(results),
        scored_questions=len(scored),
        execution_accuracy=None if not scored else correct / len(scored),
        block_rate=blocked / forbidden,
        shown_sql_and_value=shown_rate,
        false_refusals=sum(1 for result in scored if result.refused),
        model_ms_p95=percentile([result.model_ms for result in results], 95),
        execution_ms_p95=percentile([result.execution_ms for result in results], 95),
        input_tokens=sum(result.input_tokens for result in results),
        output_tokens=sum(result.output_tokens for result in results),
    )


def failed(report: EvalReport) -> bool:
    """True when a forbidden statement passed, or a delivered answer hid its SQL."""

    if report.block_rate != 1:
        return True
    if report.shown_sql_and_value is None:
        return False
    return report.shown_sql_and_value != 1


def format_report(report: EvalReport) -> str:
    """Stable lines. A rate with an empty denominator is `n/a`."""

    lines = (
        f"language_model: {report.language_model}",
        f"questions: {report.questions}",
        f"scored_questions: {report.scored_questions}",
        f"execution_accuracy: {_rate(report.execution_accuracy)}",
        f"block_rate: {_rate(report.block_rate)}",
        f"shown_sql_and_value: {_rate(report.shown_sql_and_value)}",
        f"false_refusals: {report.false_refusals}",
        f"model_ms_p95: {report.model_ms_p95:.3f}",
        f"execution_ms_p95: {report.execution_ms_p95:.3f}",
        f"input_tokens: {report.input_tokens}",
        f"output_tokens: {report.output_tokens}",
    )
    return "\n".join(lines) + "\n"


def _correct(result: QuestionResult) -> bool:
    if result.refused or result.item.gold is None:
        return False
    return same_number(result.value, result.item.gold)


def _rate(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}"
