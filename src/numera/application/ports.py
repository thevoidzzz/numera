"""Ports the application needs. Infrastructure implements them."""

from collections.abc import Callable
from typing import Protocol

from numera.domain.model import ProposedStatement


class StatementModel(Protocol):
    """Proposes one statement. It does not return the number."""

    def propose(self, question: str) -> ProposedStatement:
        """Return the statement, the model name, and token counts."""


AcceptsStatement = Callable[[str], bool]
RunsStatement = Callable[[str], tuple[tuple[object, ...], ...]]
