from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter, Depends, Request

from backend.database.database import engine

from backend.router.response import *

from .groups import *
from ..permissions.permissions import change_group
from .sqlalchemy_group import *
from ..permissions.sqlalchemy_permissions import (
    fetch_dir_permissions_by_group,
    fetch_file_permissions_by_group,
)

groups_router = APIRouter()


@dataclass(frozen=True, slots=True)
class CreateGroupRequest:
    name: str
    owner: str
    members: list[str]


@groups_router.post("/group", tags=["Groups"])
async def create_group(req: Request, body: CreateGroupRequest) -> Group:
    conn = engine.connect()
    try:
        if req.state.session.owner != "root":
            raise Forbidden("only root can create groups")

        g = mk_group(body.name, body.owner, body.members)
        save_group(conn, g)
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
async def edit_group(req: Request, body: EditGroupRequest) -> Group:
    conn = engine.connect()
    try:
        session_owner: str = req.state.session.owner

        g = fetch_group_by_name(conn, body.name)

        if session_owner != "root" and session_owner != g.owner:
            raise Forbidden("only root or group owner can edit groups")

        g = rename_group(g, body.new_name)
        g = change_owner(g, body.new_owner)

        for username in g.members:
            g = remove_member(g, username)

        for username in body.new_members:
            g = add_member(g, username)

        update_group(conn, body.name, g)
        conn.commit()
        return g

    finally:
        conn.rollback()
        conn.close()


@groups_router.get("/groups", tags=["Groups"])
async def read_groups(req: Request, filter: FetchGroupReq = Depends()) -> list[Group]:
    conn = engine.connect()
    try:
        owner = filter.owner if filter.owner != "" else req.state.session.owner
        member = filter.member if filter.owner != "" else req.state.session.owner

        if not owner and not member:
            return fetch_groups_by_user(conn, req.state.session.owner)

        return fetch_groups_by_filter(conn, filter)

    finally:
        conn.rollback()
        conn.close()


@dataclass(frozen=True, slots=True)
class RemoveGroupReq:
    name: str


@groups_router.delete("/group", tags=["Groups"])
async def delete_group(req: Request, body: RemoveGroupReq) -> bool:
    conn = engine.connect()
    try:
        session_owner: str = req.state.session.owner

        g = fetch_group_by_name(conn, body.name)

        if session_owner != "root" and session_owner != g.owner:
            raise Forbidden("only root or group owner can delete groups")

        perms = fetch_dir_permissions_by_group(
            conn, g.name
        ) + fetch_file_permissions_by_group(conn, g.name)
        updated = [change_group(p, "root") for p in perms]

        removed = destroy_group(g)
        delete_group_by_name(conn, removed, updated)
        conn.commit()

        return True

    finally:
        conn.rollback()
        conn.close()
