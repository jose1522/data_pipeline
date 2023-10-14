import json
from typing import Optional, Union

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from util.logger import get_logger


class RecordNotFound(Exception):
    def __init__(self, record_id: str):
        self.record_id = record_id
        self.message = f"Record with id {record_id} not found"
        super().__init__(self.message)


class RecordAlreadyExists(Exception):
    def __init__(self, data: Optional[dict] = None):
        self.data = json.dumps(data)
        self.message = "Record already exists"
        super().__init__(self.message)


class RecordNotActive(Exception):
    def __init__(self, record_id: str):
        self.record_id = record_id
        self.message = f"Record with id {record_id} is not active"
        super().__init__(self.message)


class BadForeignKey(Exception):
    def __init__(self, fk_id: str, fk_name: str):
        self.fk_id = fk_id
        self.fk_name = fk_name
        self.message = f"Foreign key {fk_name} with id {fk_id} does not exist"
        super().__init__(self.message)


class DatabaseError(Exception):
    def __init__(self, message: str, data: Optional[Union[dict, list]] = None):
        self.data = json.dumps(data)
        self.message = f"{message}. Record data: {self.data}"
        super().__init__(self.message)


def override_default_handlers(app: FastAPI):
    logger = get_logger()

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        content = {"detail": exc.errors(), "body": exc.body}
        logger.error(f"{request.method} {request.url} Error Response: {content}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder(content),
        )
