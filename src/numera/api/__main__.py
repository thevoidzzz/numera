"""Process entrypoint. Wires the reader and the stand-in. No paid key."""

import os

from numera.api.app import create_app
from numera.infrastructure.reader import Reader
from numera.infrastructure.sql_gate import review_statement
from numera.infrastructure.stand_in import StandInModel


def app_from_env():
    """Build the API from DATABASE_URL. The warehouse is not reloaded."""

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")
    return create_app(StandInModel(), review_statement, Reader(database_url).run)


def main() -> None:
    import uvicorn

    uvicorn.run(app_from_env(), host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
