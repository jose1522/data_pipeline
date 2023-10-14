import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from util.exceptions import (
    RecordNotFound,
    RecordAlreadyExists,
    RecordNotActive,
    DatabaseError,
)
from util.logger import get_logger


class ExceptionMiddleware(BaseHTTPMiddleware):
    """Middleware to catch exceptions and return a JSON response"""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except RecordNotFound as exc:
            return JSONResponse(status_code=404, content={"detail": str(exc)})
        except RecordAlreadyExists as exc:
            return JSONResponse(status_code=409, content={"detail": str(exc)})
        except RecordNotActive as exc:
            return JSONResponse(status_code=410, content={"detail": str(exc)})
        except DatabaseError as exc:
            return JSONResponse(status_code=500, content={"detail": str(exc)})
        except Exception as exc:
            return JSONResponse(
                status_code=500, content={"detail": f"An error occurred: {str(exc)}"}
            )
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable):
        super().__init__(app)
        self.logger = get_logger()

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        try:
            response = await call_next(request)
            response_time = time.time() - start
            self.logger.info(
                f"Request: {request.method} {request.url} {response.status_code} - {response_time:.2f}s"
            )
            return response
        except Exception as exc:
            self.logger.exception(
                f"Request: {request.method} {request.url}. An error occurred: {exc}"
            )
