from __future__ import annotations
from fastapi import Request, HTTPException

from backend.auth.session.redis_sessions import fetch_session_by_id


class UnauthorizedException(HTTPException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(status_code=401, detail=message)


async def auth_middleware(request: Request) -> None:
    token = request.cookies.get("access_token", "")

    try:
        session = fetch_session_by_id(token)
        request.state.session = session
    except ValueError:
        raise UnauthorizedException("you are not authorized")
