#
from __future__ import annotations

import logging
import traceback
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class APIException(Exception):
    """
    Base application exception.
    """

    status_code = 500

    error = "internal_error"

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:

        self.message = message

        self.details = details or {}

        super().__init__(message)
class BadRequest(APIException):

    status_code = 400

    error = "bad_request"


class Unauthorized(APIException):

    status_code = 401

    error = "unauthorized"


class Forbidden(APIException):

    status_code = 403

    error = "forbidden"


class NotFound(APIException):

    status_code = 404

    error = "not_found"


class Conflict(APIException):

    status_code = 409

    error = "conflict"


class Validation(APIException):

    status_code = 422

    error = "validation_error"


class RateLimited(APIException):

    status_code = 429

    error = "rate_limited"


class Internal(APIException):

    status_code = 500

    error = "internal_error"


class ServiceUnavailable(APIException):

    status_code = 503

    error = "service_unavailable"
def error_response(
    *,
    status_code: int,
    error: str,
    message: str,
    details: dict[str, Any] | None = None,
):

    return JSONResponse(

        status_code=status_code,

        content={

            "success": False,

            "error": {

                "id": str(uuid.uuid4()),

                "type": error,

                "message": message,

                "details": details or {},
            },
        },
    )
async def api_exception_handler(
    request: Request,
    exc: APIException,
):

    logger.warning(

        "%s %s -> %s",

        request.method,

        request.url.path,

        exc.message,
    )

    return error_response(

        status_code=exc.status_code,

        error=exc.error,

        message=exc.message,

        details=exc.details,
    )
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):

    logger.warning(

        "%s %s -> %s",

        request.method,

        request.url.path,

        exc.detail,
    )

    return error_response(

        status_code=exc.status_code,

        error="http_error",

        message=str(exc.detail),
    )
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):

    error_id = str(uuid.uuid4())

    logger.error(

        "Unhandled exception %s\n%s",

        error_id,

        traceback.format_exc(),
    )

    return JSONResponse(

        status_code=500,

        content={

            "success": False,

            "error": {

                "id": error_id,

                "type": "internal_error",

                "message": "An unexpected error occurred.",
            },
        },
    )   
def register_exception_handlers(
    app: FastAPI,
):

    app.add_exception_handler(

        APIException,

        api_exception_handler,
    )

    app.add_exception_handler(

        HTTPException,

        http_exception_handler,
    )

    app.add_exception_handler(

        Exception,

        unhandled_exception_handler,
    )