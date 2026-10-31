"""Failures a caller can handle without a driver traceback."""


class PrivilegeError(Exception):
    """The reader role cannot run this statement. Do not retry as the owner."""


class DatabaseUnavailable(Exception):
    """The warehouse cannot be reached. The message has no connection string."""


class StatementFailed(Exception):
    """The database did not return a table for this statement."""


class RequestError(ValueError):
    """The question cannot be accepted."""


class ModelSchemaError(Exception):
    """The model response did not match the schema."""


class ModelTimeout(Exception):
    """The model did not respond in time."""


class EvalError(ValueError):
    """The evaluation set cannot be scored."""
