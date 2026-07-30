from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter, Depends, Request

import backend.database.database as db
import backend.router.response as resp
from . import groups as grps, sqlalchemy_group as grps_src

groups_router = APIRouter()


@dataclass(frozen=True, slots=True)
class CreateGroupRequest:
    name: str
    owner: str
    members: list[str]


@groups_router.post("/group", tags=["Groups"])
async def create_group(req: Request, body: CreateGroupRequest) -> grps.Group:
    conn = db.engine.connect()
    try:
        if req.state.session.owner != "root":
            raise resp.Forbidden("only root can create groups")

        g = grps.mk_group(body.name, body.owner, body.members)
        conn = grps_src.save_group(conn, g)
        conn.commit()
        return g

    finally:
        conn.rollback()
        conn.close()


@dataclass(frozen=True, slots=True)
class EditGroupRequest:
    name: str
    new_name: str
    new_owner: str
    new_members: list[str]


@groups_router.patch("/group", tags=["Groups"])
async def edit_group(req: Request, body: EditGroupRequest) -> grps.Group:
    conn = db.engine.connect()
    try:
        session_owner: str = req.state.session.owner

        g = grps_src.fetch_group_by_name(conn, body.name)

        if session_owner != "root" and session_owner != g.owner:
            raise resp.Forbidden("only root or group owner can edit groups")

        g = grps.rename_group(g, body.new_name)
        g = grps.change_owner(g, body.new_owner)

        for username in g.members:
            g = grps.remove_member(g, username)

        for username in body.new_members:
            g = grps.add_member(g, username)

        conn = grps_src.update_group(conn, body.name, g)
        conn.commit()
        return g

    finally:
        conn.rollback()
        conn.close()


@groups_router.get("/groups", tags=["Groups"])
async def read_groups(
    req: Request, filter: grps.FetchGroupReq = Depends()
) -> list[grps.Group]:
    conn = db.engine.connect()
    try:
        owner = filter.owner if filter.owner != "" else req.state.session.owner
        member = filter.member if filter.owner != "" else req.state.session.owner

        if not owner and not member:
            return grps_src.fetch_groups_by_user(conn, req.state.session.owner)

        return grps_src.fetch_groups_by_filter(conn, filter)

    finally:
        conn.rollback()
        conn.close()


@dataclass(frozen=True, slots=True)
class RemoveGroupReq:
    name: str


@groups_router.delete("/group", tags=["Groups"])
async def delete_group(req: Request, body: RemoveGroupReq) -> bool:
    conn = db.engine.connect()
    try:
        session_owner: str = req.state.session.owner

        g = grps_src.fetch_group_by_name(conn, body.name)

        if session_owner != "root" and session_owner != g.owner:
            raise resp.Forbidden("only root or group owner can delete groups")

        removed = grps.destroy_group(g)
        conn = grps_src.delete_group_by_name(conn, removed)
        conn.commit()

        return True

    finally:
        conn.rollback()
        conn.close()
