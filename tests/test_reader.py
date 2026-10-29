"""The reader role can recompute a total and cannot change the warehouse."""

from decimal import Decimal

import psycopg
import pytest
from psycopg.errors import InsufficientPrivilege

from numera.infrastructure.warehouse import load_warehouse, reader_database_url

_WEST_MARCH_REVENUE = """
SELECT SUM(amount)
FROM warehouse.journal_line
WHERE entity_code = 'WEST'
  AND account_code = '4000'
  AND period_code = '2026-03'
"""

_WRITES = [
    """
    INSERT INTO warehouse.journal_line
        (line_id, entity_code, account_code, period_code, amount, memo)
    VALUES (99, 'WEST', '4000', '2026-03', 1.00, 'not allowed')
    """,
    "UPDATE warehouse.journal_line SET amount = 0",
    "DELETE FROM warehouse.journal_line",
    "DROP TABLE warehouse.journal_line",
    "CREATE TABLE warehouse.blocked (id integer)",
]


def test_reader_selects_the_seeded_total_with_a_two_second_timeout(database_url: str) -> None:
    load_warehouse(database_url)

    with psycopg.connect(reader_database_url(database_url)) as conn:
        value = conn.execute(_WEST_MARCH_REVENUE).fetchone()[0]
        timeout = conn.execute("SHOW statement_timeout").fetchone()[0]

    assert value == Decimal("1750.50")
    assert timeout == "2s"


@pytest.mark.parametrize("statement", _WRITES)
def test_reader_cannot_change_the_warehouse(database_url: str, statement: str) -> None:
    load_warehouse(database_url)

    with psycopg.connect(reader_database_url(database_url)) as conn:
        with pytest.raises(InsufficientPrivilege):
            conn.execute(statement)


def test_seed_is_not_loaded_through_the_reader(database_url: str) -> None:
    load_warehouse(database_url)

    with pytest.raises(InsufficientPrivilege):
        load_warehouse(reader_database_url(database_url))
