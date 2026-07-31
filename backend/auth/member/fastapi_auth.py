from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter, Request, Response, Depends
import json
import base64

import backend.database.database as db
import backend.router.response as resp
from ..session import session as ssns, redis_sessions as ssns_rds
from . import member as mbrs, sqlalchemy_member as mbrs_src
from ...file_manager.groups import groups as grps, sqlalchemy_group as grps_src

auth_router = APIRouter()


@dataclass(frozen=True, slots=True)
class LoginRequest:
    username: str
    password: str


@auth_router.post("/auth/login", tags=["Auth"])
async def login(body: LoginRequest, response: Response) -> bool:
    conn = db.engine.connect()
    try:
        member = mbrs_src.fetch_member_by_username(conn, body.username)
        member = mbrs.is_password_incorect(member, body.password)
        ssn = ssns.generate_session_for(member.username)

        user_session = ssns_rds.save_session(ssn)

        user_data = {
            "username": member.username,
            "is_root": True if member.username == "root" else False,
        }

        json_user_data = base64.b64encode(json.dumps(user_data).encode("utf-8")).decode(
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
        raise resp.BadRequest("incorrect username or password")
    finally:
        conn.close()


@auth_router.post("/auth/logout", tags=["Auth"])
def logout(request: Request, response: Response) -> bool:
    access_token = request.cookies.get("access_token", "")

    ssn = ssns_rds.fetch_session_by_id(access_token)
    ssns_rds.close_session(ssn)

    response.delete_cookie(key="access_token", secure=True, samesite="strict")
    response.delete_cookie(key="user_data", samesite="strict")

    return True


@dataclass(frozen=True, slots=True)
class RegisterRequest:
    username: str
    password: str


@auth_router.post("/auth/register", tags=["Auth"])
def register(body: RegisterRequest) -> bool:
    conn = db.engine.connect()
    try:
        candidate = mbrs.make_candidate(body.username, body.password)
        group = grps.mk_group(candidate.username, candidate.username, [body.username])

        conn = mbrs_src.save_candidate(conn, candidate)
        conn = grps_src.save_group(conn, group)
        conn.commit()

        return True
    finally:
        conn.close()
