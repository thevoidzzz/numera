"""Print the evaluation report. Requires DATABASE_URL and does not call a hosted model."""

import os
import sys

from numera.application.evaluate import evaluate
from numera.domain.errors import EvalError
from numera.domain.scoring import failed, format_report
from numera.eval.load import load_questions
from numera.infrastructure.forbidden import load_forbidden
from numera.infrastructure.reader import Reader
from numera.infrastructure.sql_gate import review_statement
from numera.infrastructure.stand_in import StandInModel
from numera.infrastructure.warehouse import load_warehouse


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")
    load_warehouse(database_url)
    try:
        report = evaluate(
            StandInModel(),
            review_statement,
            Reader(database_url).run,
            load_questions(),
            tuple(sql for _, sql in load_forbidden()),
        )
    except EvalError as exc:
        raise SystemExit(str(exc)) from exc
    sys.stdout.write(format_report(report))
    if failed(report):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
