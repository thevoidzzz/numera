"""Question set for the evaluation command. Statements live with the stand-in, not here."""

import json
from pathlib import Path

from numera.domain.scoring import QuestionItem


def load_questions() -> tuple[QuestionItem, ...]:
    raw = json.loads((Path(__file__).resolve().parent / "questions.json").read_text(encoding="utf-8"))
    return tuple(QuestionItem(item["id"], item["question"], item["gold"]) for item in raw)
