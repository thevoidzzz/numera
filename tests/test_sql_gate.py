"""The versioned forbidden set fails closed, before any statement reaches the database."""

import pytest

from numera.infrastructure.forbidden import load_forbidden
from numera.infrastructure.sql_gate import MAX_STATEMENT_LENGTH, review_statement

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


def test_forbidden_set_has_every_form() -> None:
    assert {name for name, _ in load_forbidden()} == _FORMS


@pytest.mark.parametrize(("name", "statement"), load_forbidden(), ids=[name for name, _ in load_forbidden()])
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
