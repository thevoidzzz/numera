"""Load the synthetic warehouse. Only the owner connection writes."""

from pathlib import Path
from urllib.parse import urlparse, urlunparse

import psycopg

_DIR = Path(__file__).resolve().parent
READER_ROLE = "numera_reader"


def load_warehouse(database_url: str) -> None:
    """Replace the warehouse schema with the versioned seed, then grant the reader."""

    schema = (_DIR / "schema.sql").read_text(encoding="utf-8")
    seed = (_DIR / "seed.sql").read_text(encoding="utf-8")
    reader = (_DIR / "reader.sql").read_text(encoding="utf-8")
    with psycopg.connect(database_url) as conn:
        conn.execute(schema)
        conn.execute(seed)
    with psycopg.connect(database_url, autocommit=True) as conn:
        conn.execute(reader)


def reader_database_url(database_url: str) -> str:
    """Same database, reader role, no password."""

    parsed = urlparse(database_url)
    host = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    return urlunparse(parsed._replace(netloc=f"{READER_ROLE}@{host}{port}"))
