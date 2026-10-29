"""Load the synthetic warehouse. Only the owner connection writes."""

from pathlib import Path

import psycopg

_DIR = Path(__file__).resolve().parent


def load_warehouse(database_url: str) -> None:
    """Replace the warehouse schema with the versioned seed."""

    schema = (_DIR / "schema.sql").read_text(encoding="utf-8")
    seed = (_DIR / "seed.sql").read_text(encoding="utf-8")
    with psycopg.connect(database_url) as conn:
        conn.execute(schema)
        conn.execute(seed)
