# Numera

Natural-language questions over a read-only finance warehouse. A question counts when the executed result matches the number, and the response shows the SQL that ran.

## Tests

GitHub Actions runs `pytest` on pull requests and on pushes to `main`. The job installs no model client and uses no API key.

The local database is PostgreSQL 16.

```bash
pip install -e ".[dev]"
DATABASE_URL=postgresql://numera@localhost:5432/numera pytest
```

## Contributing

Open a pull request against `main`. The `test` check has to pass before merge.

Architecture and decisions live in `docs/architecture/` and `docs/adr/`.
