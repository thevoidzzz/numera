"""Deterministic statement proposer. It has no API key and does not invent a total."""

import json
from pathlib import Path

from numera.domain.errors import ModelSchemaError
from numera.domain.model import ProposedStatement

MODEL_NAME = "sql-stand-in"
_STATEMENTS = json.loads((Path(__file__).resolve().parent / "statements.json").read_text(encoding="utf-8"))


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
