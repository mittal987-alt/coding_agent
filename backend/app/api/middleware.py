#
from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)
class RequestIDMiddleware(BaseHTTPMiddleware):

    HEADER_NAME = "X-Request-ID"

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:

        request_id = request.headers.get(
            self.HEADER_NAME,
            str(uuid.uuid4()),
        )

        request.state.request_id = request_id

        response = await call_next(request)

        response.headers[
            self.HEADER_NAME
        ] = request_id

        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:

        start = time.perf_counter()

        response = await call_next(request)

        duration = (
            time.perf_counter() - start
        ) * 1000

        logger.info(

            "%s %s %d %.2f ms",

            request.method,

            request.url.path,

            response.status_code,

            duration,
        )

        return response
class TimingMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:

        start = time.perf_counter()

        response = await call_next(request)

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        response.headers[
            "X-Process-Time"
        ] = f"{elapsed:.2f}"

        return response
class SecurityHeadersMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:

        response = await call_next(request)

        response.headers[
            "X-Content-Type-Options"
        ] = "nosniff"

        response.headers[
            "X-Frame-Options"
        ] = "DENY"

        response.headers[
            "Referrer-Policy"
        ] = "strict-origin"

        response.headers[
            "X-XSS-Protection"
        ] = "1; mode=block"

        return response
class RateLimitMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:

        #
        # Future:
        #
        # Redis
        # Token Bucket
        # Sliding Window
        #

        return await call_next(request)

def register_middleware(
    app: FastAPI,
) -> None:

    app.add_middleware(
        RequestIDMiddleware,
    )

    app.add_middleware(
        TimingMiddleware,
    )

    app.add_middleware(
        RequestLoggingMiddleware,
    )

    app.add_middleware(
        SecurityHeadersMiddleware,
    )

    app.add_middleware(
        RateLimitMiddleware,
    )

def register_cors(
    app: FastAPI,
    *,
    origins: list[str],
    allow_credentials: bool = True,
) -> None:

    app.add_middleware(

        CORSMiddleware,

        allow_origins=origins,

        allow_credentials=allow_credentials,

        allow_methods=["*"],

        allow_headers=["*"],
    )   