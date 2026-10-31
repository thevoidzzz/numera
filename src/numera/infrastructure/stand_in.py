"""Deterministic statement proposer. It has no API key and does not invent a total."""

from numera.domain.errors import ModelSchemaError
from numera.domain.model import ProposedStatement

MODEL_NAME = "sql-stand-in"

_STATEMENTS = {
    "What is West desk revenue for March 2026?": (
        "SELECT SUM(amount) FROM warehouse.journal_line "
        "WHERE entity_code = 'WEST' AND account_code = '4000' AND period_code = '2026-03'"
    ),
    "Drop the journal lines.": "DROP TABLE warehouse.journal_line",
}


class StandInModel:
    """Looks up a hand-written statement. An unknown question is a schema miss."""

    def propose(self, question: str) -> ProposedStatement:
        sql = _STATEMENTS.get(question)
        if sql is None:
            raise ModelSchemaError("the stand-in has no statement for this question")
        return ProposedStatement(
            sql=sql,
            model=MODEL_NAME,
            input_tokens=len(question.split()),
            output_tokens=len(sql.split()),
        )
