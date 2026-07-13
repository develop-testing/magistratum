from __future__ import annotations
from fastapi import Request, HTTPException
from result import Ok

from auth.shell.sources.redis_sessions import *
from router.response import *


class UnauthorizedException(HTTPException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(status_code=401, detail=message)


async def auth_middleware(request: Request) -> None:
    token = request.cookies.get("access_token", "")

    match fetch_session_by_id(token):
        case Ok(session):
            request.state.session = session
        case _:
            raise UnauthorizedException("you are not authorized")
