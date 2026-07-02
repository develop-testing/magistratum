from __future__ import annotations
from fastapi import Request, HTTPException
from result import Ok

from auth.redis_sessions import *
from .response import *


class UnauthorizedException(HTTPException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(status_code=401, detail=message)


async def auth_middleware(request: Request) -> bool:
    token = request.cookies.get("access_token", "")

    match fetch_session_by_id(token):
        case Ok():
            return True
        case _:
            raise UnauthorizedException("you are not authorized")
