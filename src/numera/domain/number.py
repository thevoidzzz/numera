"""A score is one numeric cell. NULL is a value. A table is not clipped into a score."""

from collections.abc import Sequence
from decimal import Decimal


def one_decimal(rows: Sequence[Sequence[object]]) -> tuple[bool, Decimal | None]:
    """Return whether the rows are one number, and that number.

    A NULL cell is a number that is absent. Zero rows, two rows, two columns,
    or a non-numeric cell is not a number.
    """

    if len(rows) != 1 or len(rows[0]) != 1:
        return False, None
    cell = rows[0][0]
    if cell is None:
        return True, None
    if isinstance(cell, bool) or not isinstance(cell, (int, Decimal)):
        return False, None
    return True, Decimal(cell)
