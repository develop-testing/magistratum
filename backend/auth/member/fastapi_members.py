from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter, Request, Depends

import backend.database.database as db
import backend.router.response as resp
from . import member as mbrs, sqlalchemy_member as member_src

member_router = APIRouter()


MemberFilter = mbrs.FilterOfMember
MembersRes = list[mbrs.MemberProfile]


@member_router.get("/members", tags=["Members"])
def fetch_members(fltr: MemberFilter = Depends()) -> MembersRes:
    conn = db.engine.connect()
    try:
        return member_src.fetch_members_by_filter(conn, fltr)
    finally:
        conn.close()


@dataclass(frozen=True, slots=True)
class RemoveMemberReq:
    username: str


@member_router.delete("/members/", tags=["Members"])
def remove_member(req: Request, body: RemoveMemberReq) -> bool:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner

        if session_owner != "root" and session_owner != body.username:
            raise resp.Forbidden("access not allowed")

        conn = member_src.delete_member_by_username(conn, body.username)
        conn.commit()

        return True
    except member_src.DeleteError as err:
        raise resp.BadRequest(str(err))
    finally:
        conn.close()
