"""The versioned forbidden set fails closed, before any statement reaches the database."""

from pathlib import Path

import pytest

from numera.infrastructure.sql_gate import MAX_STATEMENT_LENGTH, review_statement

_FORBIDDEN = Path(__file__).resolve().parents[1] / "src" / "numera" / "infrastructure" / "forbidden.txt"
_FORMS = frozenset(
    {
        "alter",
        "blank",
        "call",
        "copy",
        "create",
        "delete",
        "do",
        "double_semicolon",
        "drop",
        "empty",
        "explain",
        "grant",
        "insert",
        "insert_cte",
        "lock",
        "merge",
        "revoke",
        "select_into",
        "set",
        "set_role",
        "show",
        "truncate",
        "two_statements",
        "unparseable",
        "update",
        "values",
    }
)

_READS = [
    "SELECT SUM(amount) FROM warehouse.journal_line",
    "SELECT 1;",
    "WITH lines AS (SELECT amount FROM warehouse.journal_line) SELECT SUM(amount) FROM lines",
    "SELECT 1 UNION SELECT 2",
    "SELECT 1 INTERSECT SELECT 1",
    "SELECT 1 EXCEPT SELECT 2",
]


def _forbidden() -> list[tuple[str, str]]:
    text = _FORBIDDEN.read_text(encoding="utf-8")
    if text.endswith("\n"):
        text = text[:-1]
    cases = []
    for block in text.split("\n---\n"):
        name, sql = block.split("\n", 1)
        cases.append((name, sql))
    return cases


def test_forbidden_set_has_every_form() -> None:
    assert {name for name, _ in _forbidden()} == _FORMS


@pytest.mark.parametrize(("name", "statement"), _forbidden(), ids=[name for name, _ in _forbidden()])
def test_forbidden_statement_is_rejected(name: str, statement: str) -> None:
    assert review_statement(statement) is False


@pytest.mark.parametrize("statement", _READS)
def test_one_read_is_accepted(statement: str) -> None:
    assert review_statement(statement) is True


def test_statement_longer_than_4000_characters_is_rejected_before_it_can_pass() -> None:
    accepted = "SELECT 1" + (" " * (MAX_STATEMENT_LENGTH - len("SELECT 1")))
    assert len(accepted) == MAX_STATEMENT_LENGTH
    assert review_statement(accepted) is True
    assert review_statement(accepted + " ") is False
