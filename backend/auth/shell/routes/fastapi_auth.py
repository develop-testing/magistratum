from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter, Request, Response, Depends

from backend.router.response import *
from ...session import *
from ...member import *
from ..sources.sqlalchemy_member import *
from ..sources.redis_sessions import *

auth_router = APIRouter()


@dataclass(frozen=True, slots=True)
class LoginRequest:
    username: str
    password: str


@auth_router.post("/auth/login", tags=["Auth"])
async def login(body: LoginRequest, response: Response) -> bool:
    try:
        member = fetch_member_by_username(body.username)
    except ValueError:
        raise BadRequest("incorrect username or password")
    member = is_password_incorect(member, body.password)
    ssn = generate_session_for(member.username)
    us = save_session(ssn)
    response.set_cookie(
        key="access_token",
        value=us.id,
        httponly=True,
        secure=True,
        samesite="strict",
        expires=us.expires,
    )
    return True


@auth_router.post("/auth/logout", tags=["Auth"])
def logout(request: Request, response: Response) -> bool:
    access_token = request.cookies.get("access_token", "")
    ssn = fetch_session_by_id(access_token)
    close_session(ssn)
    response.delete_cookie(key="access_token", secure=True, samesite="strict")
    return True


@dataclass(frozen=True, slots=True)
class RegisterRequest:
    username: str
    password: str


@auth_router.post("/auth/register", tags=["Auth"])
def register(body: RegisterRequest) -> bool:
    cnd = make_candidate(body.username, body.password)
    save_candidate(cnd)
    return True
