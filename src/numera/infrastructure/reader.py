"""Execute one statement as the reader. A privilege error is not retried as the owner."""

import psycopg

from numera.domain.errors import DatabaseUnavailable, PrivilegeError, StatementFailed
from numera.infrastructure.warehouse import reader_database_url

_ROW_LIMIT = 2


class Reader:
    """Opens the reader role, fetches at most two rows, and closes."""

    def __init__(self, database_url: str) -> None:
        self._url = reader_database_url(database_url)

    def run(self, statement: str) -> tuple[tuple[object, ...], ...]:
        try:
            with psycopg.connect(self._url) as conn:
                cursor = conn.execute(statement)
                if cursor.description is None:
                    raise StatementFailed("the statement did not return a table")
                return tuple(tuple(row) for row in cursor.fetchmany(_ROW_LIMIT))
        except psycopg.errors.InsufficientPrivilege:
            raise PrivilegeError("the reader cannot run this statement") from None
        except psycopg.OperationalError:
            raise DatabaseUnavailable("the warehouse is unavailable") from None
        except psycopg.Error:
            raise StatementFailed("the statement did not return a table") from None
