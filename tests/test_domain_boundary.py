"""The domain package stays free of drivers. The architecture test is the lock."""

import ast
from pathlib import Path

_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "numera"
_ROOTS = (_PACKAGE / "domain", _PACKAGE / "application")
_FORBIDDEN_PREFIXES = (
    "numera.infrastructure",
    "numera.api",
    "fastapi",
    "psycopg",
    "sqlalchemy",
    "sqlglot",
    "httpx",
    "openai",
)
_API_FORBIDDEN_PREFIXES = ("psycopg", "sqlalchemy", "sqlglot", "openai")


def test_domain_does_not_import_infrastructure_or_the_api() -> None:
    violations = _imports(_ROOTS, _FORBIDDEN_PREFIXES)
    violations.extend(_imports((_PACKAGE / "api",), _API_FORBIDDEN_PREFIXES))
    assert violations == []


def _imports(roots, prefixes: tuple[str, ...]) -> list[str]:
    violations: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                modules: list[str] = []
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module is not None:
                    modules = [node.module]
                for module in modules:
                    if module.startswith(prefixes):
                        violations.append(f"{path.name} imports {module}")
    return violations
