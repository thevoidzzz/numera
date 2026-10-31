# Numera

Natural-language questions over a read-only finance warehouse. A question counts when the executed result matches the number, and the response shows the SQL that ran.

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

## Contributing

Open a pull request against `main`. The `test` check has to pass before merge.

Architecture and decisions live in `docs/architecture/` and `docs/adr/`.
