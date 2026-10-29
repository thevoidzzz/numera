"""The seeded warehouse has totals a person can recompute."""

from decimal import Decimal

import psycopg

from numera.infrastructure.warehouse import load_warehouse


def test_west_march_revenue_is_the_seeded_total(database_url: str) -> None:
    load_warehouse(database_url)

    with psycopg.connect(database_url) as conn:
        value = conn.execute(
            """
            SELECT SUM(amount)
            FROM warehouse.journal_line
            WHERE entity_code = 'WEST'
              AND account_code = '4000'
              AND period_code = '2026-03'
            """
        ).fetchone()[0]

    assert value == Decimal("1750.50")
