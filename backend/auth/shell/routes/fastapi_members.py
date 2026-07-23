from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter, Request, Depends

from backend.router.response import *
from ...member import *
from ..sources.sqlalchemy_member import *


member_router = APIRouter()


@member_router.get("/members", tags=["Members"])
def fetch_members(fltr: FilterOfMember = Depends()) -> list[MemberProfile]:
    res = fetch_members_by_filter(fltr)
    return res


@dataclass(frozen=True, slots=True)
class RemoveMemberReq:
    username: str


@member_router.delete("/members/", tags=["Members"])
def remove_member(req: Request, body: RemoveMemberReq) -> bool:
    try:
        session_owner = req.state.session.owner
        
        if session_owner != "root" and session_owner != body.username:
            raise Forbidden("access not allowed")

        delete_member_by_username(body.username)

        return True
    except DeleteError as err:
        raise BadRequest(str(err))

    