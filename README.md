# Numera

Natural-language questions over a read-only finance warehouse. A question counts when the executed result matches the number, and the response shows the SQL that ran.

## Evaluation

```bash
DATABASE_URL=postgresql://numera@localhost:5432/numera python -m numera.eval
```

Run on 2026-10-30 with `sql-stand-in`. The stand-in looks up a hand-written statement for each question. A hosted model would be a separate dated run. Forty-eight questions have a gold decimal. The West desk headcount is not a column, and the desk name is not a number, so those two questions stay outside execution accuracy. The block rate is the forbidden SQL file. The command exits with an error when that rate is not 1, or when a delivered answer has no SQL.

```
language_model: sql-stand-in
questions: 50
scored_questions: 48
execution_accuracy: 1.000
block_rate: 1.000
shown_sql_and_value: 1.000
false_refusals: 0
model_ms_p95: 0.013
execution_ms_p95: 5.216
input_tokens: 419
output_tokens: 569
```

## Tests

GitHub Actions runs `pytest` on pull requests and on pushes to `main`. The job installs no model client and uses no API key.

The local database is PostgreSQL 16.

```bash
pip install -e ".[dev]"
DATABASE_URL=postgresql://numera@localhost:5432/numera pytest
```

## API

```bash
DATABASE_URL=postgresql://numera@localhost:5432/numera python -m numera.api
```

`POST /v1/answers` with a JSON body `{"question": "..."}`. A forbidden statement or a result that is not one number is still HTTP 200. `value` is the decimal string the database returned, or `null`. Empty questions, a model timeout, a model response that is not a statement, and a database that is down are `application/problem+json`.

## Docker

```bash
docker compose run --rm --build tests
docker compose up --build api
```

The test image runs the same suite. The API listens on port 8000 and loads the seed on startup. PostgreSQL stays on the Compose network.

## Contributing

Open a pull request against `main`. The `test` check has to pass before merge.

Architecture and decisions live in `docs/architecture/` and `docs/adr/`.
