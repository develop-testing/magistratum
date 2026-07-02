from __future__ import annotations
from dataclasses import dataclass
from result import Ok, Err, Result
from fastapi import APIRouter, Request, Response


from .response import *
from auth.session import *
from auth.member import *
from auth.sqlalchemy_member import *
from auth.redis_sessions import *


auth_router = APIRouter()


@dataclass(frozen=True, slots=True)
class LoginRequest:
    username: str
    password: str


@auth_router.post("/auth/login", tags=["Auth"])
async def login(body: LoginRequest) -> Response:
    try:
        user_session = (
            fetch_member_by_username(body.username, body.password)
            .and_then(lambda m: generate_session_for(m.user_id))
            .map(lambda ssn: save_session(ssn))
        )

        match user_session:
            case Ok(s):
                response = Success(True)
                response.set_cookie(
                    key="access_token",
                    value=s.id,
                    httponly=True,
                    secure=True,
                    samesite="strict",
                    expires=s.expires,
                )

                return response
            case Err(ErrorOfIncorrectCreds() as err):
                return BadRequest(err.value)
            case Err(ErrorOfMemberValidate() as err):
                return BadRequest(err.value)
            case Err(SessionValidateErr() as err):
                return BadRequest(err.value)
            case Err(NotFoundMemberError() as err):
                return BadRequest("incorrect username or password")
            case _:
                return InternalServerError()

    except:
        return InternalServerError()


@auth_router.post("/auth/logout", tags=["Auth"])
def logout(request: Request) -> Response:
    try:
        result = fetch_session_by_id(request.cookies.get("access_token", "")).map(
            lambda ssn: close_session(ssn)
        )

        match result:
            case Ok():
                response = Success(True)
                response.delete_cookie(
                    key="access_token", secure=True, samesite="strict"
                )
            case Err(err):
                return BadRequest(err.value)

        return response
    except:
        return InternalServerError()


@dataclass(frozen=True, slots=True)
class RegisterRequest:
    username: str
    password: str


@auth_router.post("/auth/register", tags=["Auth"])
def register(body: RegisterRequest) -> Response:
    try:
        candidate = make_candidate(body.username, body.password).and_then(
            lambda cnd: save_candidate(cnd)
        )

        match candidate:
            case Ok():
                return Success(True)
            case Err(SaveDuplicateError() as err):
                return BadRequest(err.value)
            case _:
                return InternalServerError()
    except Exception as e:
        return InternalServerError()
