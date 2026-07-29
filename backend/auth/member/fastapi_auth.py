from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter, Request, Response, Depends
import json
import base64

from backend.database.database import engine
from backend.router.response import *
from ..session.session import *
from .member import *
from .sqlalchemy_member import *
from ..session.redis_sessions import *
from ...file_manager.groups.groups import mk_group
from ...file_manager.groups.sqlalchemy_group import save_group

auth_router = APIRouter()


@dataclass(frozen=True, slots=True)
class LoginRequest:
    username: str
    password: str


@auth_router.post("/auth/login", tags=["Auth"])
async def login(body: LoginRequest, response: Response) -> bool:
    conn = engine.connect()
    try:
        member = fetch_member_by_username(conn, body.username)
        member = is_password_incorect(member, body.password)
        ssn = generate_session_for(member.username)

        user_session = save_session(ssn)

        user_data: dict[str, str | bool] = {}
        user_data["username"] = member.username
        user_data["is_root"] = True if member.username == "root" else False

        json_user_data = json.dumps(user_data)
        json_user_data = base64.b64encode(json_user_data.encode("utf-8")).decode(
            "utf-8"
        )

        response.set_cookie(
            key="access_token",
            value=user_session.id,
            httponly=True,
            secure=True,
            samesite="strict",
            expires=user_session.expires,
        )

        response.set_cookie(
            key="user_data",
            value=json_user_data,
            secure=True,
            samesite="strict",
            expires=user_session.expires,
        )

        return True
    except ValueError:
        raise BadRequest("incorrect username or password")
    finally:
        conn.rollback()
        conn.close()


@auth_router.post("/auth/logout", tags=["Auth"])
def logout(request: Request, response: Response) -> bool:
    access_token = request.cookies.get("access_token", "")
    ssn = fetch_session_by_id(access_token)
    close_session(ssn)
    response.delete_cookie(key="access_token", secure=True, samesite="strict")
    response.delete_cookie(key="user_data", samesite="strict")
    return True


@dataclass(frozen=True, slots=True)
class RegisterRequest:
    username: str
    password: str


@auth_router.post("/auth/register", tags=["Auth"])
def register(body: RegisterRequest) -> bool:
    conn = engine.connect()
    try:
        cnd = make_candidate(body.username, body.password)
        group = mk_group(cnd.username, cnd.username, [body.username])

        save_candidate(conn, cnd)
        save_group(conn, group)
        conn.commit()

        return True
    finally:
        conn.rollback()
        conn.close()
