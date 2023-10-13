from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from util.exceptions import (
    RecordNotFound,
    RecordAlreadyExists,
    RecordNotActive,
    DatabaseError,
)


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
