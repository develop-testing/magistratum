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
    user_session = (
        fetch_member_by_username(body.username)
        .and_then(lambda member: is_password_incorect(member, body.password))
        .and_then(lambda member: generate_session_for(member.username))
        .map(lambda ssn: save_session(ssn))
    )

    match user_session:
        case Ok(us):
            response = Success(True)
            response.set_cookie(
                key="access_token",
                value=us.id,
                httponly=True,
                secure=True,
                samesite="strict",
                expires=us.expires,
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


@auth_router.post("/auth/logout", tags=["Auth"])
def logout(request: Request) -> Response:
    access_token = request.cookies.get("access_token", "")
    result = fetch_session_by_id(access_token).map(lambda ssn: close_session(ssn))

    match result:
        case Ok():
            response = Success(True)
            response.delete_cookie(key="access_token", secure=True, samesite="strict")
            return response
        case Err(err):
            return BadRequest(err.value)


@dataclass(frozen=True, slots=True)
class RegisterRequest:
    username: str
    password: str


@auth_router.post("/auth/register", tags=["Auth"])
def register(body: RegisterRequest) -> Response:
    member = make_candidate(body.username, body.password).and_then(
        lambda cnd: save_candidate(cnd)
    )

    match member:
        case Ok():
            return Success(True)
        case Err(SaveDuplicateError() as err):
            return BadRequest(err.value)
        case _:
            return InternalServerError()
