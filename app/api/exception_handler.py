"""Mapping of domain exceptions to HTTP responses."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    OPAAttributesServiceError,
    PrincipalNotFoundError,
    DatabaseReadError,
    DatabaseWriteError,
    AttributeConflictError,
    ExternalSourceAuthError,
    ExternalSourceRequestError,
    ExternalSourceResponseError,
)

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""

    @app.exception_handler(PrincipalNotFoundError)
    async def _principal_not_found(request: Request, exc: PrincipalNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(AttributeConflictError)
    async def _attribute_conflict(request: Request, exc: AttributeConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(DatabaseReadError)
    async def _database_read(request: Request, exc: DatabaseReadError) -> JSONResponse:
        logger.error("DatabaseReadError: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    @app.exception_handler(DatabaseWriteError)
    async def _database_write(request: Request, exc: DatabaseWriteError) -> JSONResponse:
        logger.error("DatabaseWriteError: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    @app.exception_handler(ExternalSourceAuthError)
    async def _external_auth(request: Request, exc: ExternalSourceAuthError) -> JSONResponse:
        logger.error("ExternalSourceAuthError: %s", exc)
        return JSONResponse(status_code=502, content={"detail": f"External source authentication failed: {exc.source}"})

    @app.exception_handler(ExternalSourceRequestError)
    async def _external_request(request: Request, exc: ExternalSourceRequestError) -> JSONResponse:
        logger.error("ExternalSourceRequestError: %s", exc)
        return JSONResponse(status_code=502, content={"detail": f"External source unavailable: {exc.source}"})

    @app.exception_handler(ExternalSourceResponseError)
    async def _external_response(request: Request, exc: ExternalSourceResponseError) -> JSONResponse:
        logger.error("ExternalSourceResponseError: %s", exc)
        return JSONResponse(status_code=502, content={"detail": f"Unexpected response from external source: {exc.source}"})

    @app.exception_handler(OPAAttributesServiceError)
    async def _catch_all(request: Request, exc: OPAAttributesServiceError) -> JSONResponse:
        logger.error("Unhandled service error: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
