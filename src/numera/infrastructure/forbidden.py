"""The versioned forbidden statements. Names stay with the SQL."""

from pathlib import Path


def load_forbidden() -> tuple[tuple[str, str], ...]:
    """Each block is a name and the statement the gate has to reject."""

    text = (Path(__file__).resolve().parent / "forbidden.txt").read_text(encoding="utf-8")
    if text.endswith("\n"):
        text = text[:-1]
    return tuple((name, sql) for name, sql in (block.split("\n", 1) for block in text.split("\n---\n")))
