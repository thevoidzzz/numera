"""What the model is allowed to return. A sentence with a total is not a result."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProposedStatement:
    """One statement, plus the name and token counts the report has to print."""

    sql: str
    model: str
    input_tokens: int
    output_tokens: int
