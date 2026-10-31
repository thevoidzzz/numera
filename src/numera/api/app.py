"""HTTP contract. Handlers call the use case and do not open the database."""

import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from numera.application.answer import Answer, answer_question
from numera.application.ports import AcceptsStatement, RunsStatement, StatementModel
from numera.domain.errors import DatabaseUnavailable, ModelSchemaError, ModelTimeout, RequestError

logger = logging.getLogger("numera.api")


class AnswerBody(BaseModel):
    """The question. Length is checked in the use case."""

    question: str


def create_app(model: StatementModel, accepts: AcceptsStatement, run: RunsStatement) -> FastAPI:
    """Build the API around an already chosen model, gate, and reader."""

    app = FastAPI()

    @app.middleware("http")
    async def attach_request_id(request: Request, call_next):
        request.state.request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid_body(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _problem(request, 400, "Bad Request", _validation_detail(exc))

    @app.exception_handler(RequestError)
    async def rejected_question(request: Request, exc: RequestError) -> JSONResponse:
        return _problem(request, 400, "Bad Request", str(exc))

    @app.exception_handler(ModelTimeout)
    async def timed_out(request: Request, exc: ModelTimeout) -> JSONResponse:
        return _problem(request, 504, "Gateway Timeout", "the model did not respond in time")

    @app.exception_handler(ModelSchemaError)
    async def invalid_model(request: Request, exc: ModelSchemaError) -> JSONResponse:
        return _problem(request, 502, "Bad Gateway", "the model response did not match the schema")

    @app.exception_handler(DatabaseUnavailable)
    async def warehouse_down(request: Request, exc: DatabaseUnavailable) -> JSONResponse:
        return _problem(request, 503, "Service Unavailable", "the warehouse is unavailable")

    @app.post("/v1/answers")
    def answers(body: AnswerBody, request: Request) -> dict[str, object]:
        result = answer_question(body.question, model, accepts, run)
        _log_answer(request, body.question, result)
        return _payload(request, result)

    return app


def _payload(request: Request, result: Answer) -> dict[str, object]:
    return {
        "request_id": request.state.request_id,
        "refused": result.refused,
        "reason": result.reason,
        "sql": result.sql,
        "value": None if result.value is None else format(result.value, "f"),
    }


def _log_answer(request: Request, question: str, result: Answer) -> None:
    logger.info(
        "request_id=%s model_ms=%.3f execution_ms=%.3f model=%s input_tokens=%s output_tokens=%s refused=%s row_count=%s sql=%s question=%s",
        request.state.request_id,
        result.model_ms,
        result.execution_ms,
        result.model,
        result.input_tokens,
        result.output_tokens,
        str(result.refused).lower(),
        result.row_count,
        result.sql,
        question,
    )


def _problem(request: Request, status: int, title: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        media_type="application/problem+json",
        content={
            "type": "about:blank",
            "title": title,
            "status": status,
            "detail": detail,
            "request_id": request.state.request_id,
        },
    )


def _validation_detail(exc: RequestValidationError) -> str:
    errors = exc.errors()
    if any(error.get("type") == "json_invalid" for error in errors):
        return "request body must be json"
    missing = [error.get("loc", ()) for error in errors if error.get("type") == "missing"]
    if any(isinstance(part, str) and part == "question" for loc in missing for part in loc):
        return "question is required"
    return "request body is invalid"
