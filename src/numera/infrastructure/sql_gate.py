"""One read statement may pass. Everything else stops here."""

import logging

import sqlglot
from sqlglot import exp

# The forbidden set is unsupported syntax on purpose. A warning per statement hides the report.
logging.getLogger("sqlglot").setLevel(logging.ERROR)

MAX_STATEMENT_LENGTH = 4000

_READS = (exp.Select, exp.Union, exp.Intersect, exp.Except)
_BLOCKED = (
    exp.Alter,
    exp.Command,
    exp.Copy,
    exp.Create,
    exp.Delete,
    exp.Drop,
    exp.Grant,
    exp.Insert,
    exp.Merge,
    exp.Revoke,
    exp.Set,
    exp.TruncateTable,
    exp.Update,
)


def review_statement(statement: str) -> bool:
    """True when the text is exactly one SELECT, or a set operation of SELECTs."""

    if len(statement) > MAX_STATEMENT_LENGTH:
        return False
    try:
        trees = sqlglot.parse(statement, dialect="postgres")
    except sqlglot.errors.SqlglotError:
        return False
    if len(trees) != 1 or not isinstance(trees[0], _READS):
        return False
    tree = trees[0]
    if any(node.args.get("into") is not None for node in tree.find_all(exp.Select)):
        return False
    return not any(True for _ in tree.find_all(*_BLOCKED))
