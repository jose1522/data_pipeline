import time
from typing import Callable

from sqlalchemy.exc import IntegrityError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from util.exceptions import (
    RecordNotFound,
    RecordAlreadyExists,
    RecordNotActive,
    DatabaseError,
    BadForeignKey,
)
from util.logger import get_logger


class ExceptionMiddleware(BaseHTTPMiddleware):
    """Middleware to catch exceptions and return a JSON response"""

    def __init__(self, app: Callable, *args, **kwargs):
        super().__init__(app=app, *args, **kwargs)
        self.logger = get_logger()

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except RecordNotFound as exc:
            content = {"detail": str(exc), "record_id": exc.record_id}
            self.logger.error(f"Error Response: {content}")
            return JSONResponse(status_code=404, content=content)
        except RecordAlreadyExists as exc:
            content = {"detail": str(exc), "data": exc.data}
            self.logger.error(f"Error Response: {content}")
            return JSONResponse(status_code=409, content=content)
        except RecordNotActive as exc:
            content = {"detail": str(exc), "record_id": exc.record_id}
            self.logger.error(f"Error Response: {content}")
            return JSONResponse(status_code=410, content=content)
        except DatabaseError as exc:
            content = {"detail": str(exc), "data": exc.data}
            self.logger.error(f"Error Response: {content}")
            return JSONResponse(status_code=500, content=content)
        except IntegrityError as exc:
            content = {"detail": str(exc)}
            self.logger.error(f"Error Response: {content}")
            return JSONResponse(status_code=400, content=content)
        except BadForeignKey as exc:
            content = {"detail": str(exc), "fk_id": exc.fk_id, "fk_name": exc.fk_name}
            self.logger.error(f"Error Response: {content}")
            return JSONResponse(status_code=400, content=content)
        except Exception as exc:
            content = {"detail": str(exc)}
            self.logger.error(f"Error Response: {content}. Error type: {type(exc)}")
            return JSONResponse(status_code=500, content=content)
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
