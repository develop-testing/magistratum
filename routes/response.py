from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import Response
from typing import Any


class Success(JSONResponse):
    def __init__(self, content: Any, status_code: int = 200) -> None:
        super().__init__(content=jsonable_encoder(content), status_code=status_code)


class InternalServerError(Response):
    def __init__(self) -> None:
        super().__init__(status_code=500, content="Internal Server Error")


class Forbidden(Response):
    def __init__(self, error: str = "") -> None:
        super().__init__(
            status_code=403,
            content="Forbidden" if not error else error,
        )


class BadRequest(Response):
    def __init__(self, error: str = "") -> None:
        super().__init__(
            status_code=400,
            content="Bad Request" if not error else error,
        )
