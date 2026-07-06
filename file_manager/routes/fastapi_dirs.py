from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter, Depends, Request

from router.response import *

from ..directory import (
    BrokenDirectory,
    DirFilter,
    Directory,
    change_directory_parent,
    mk_directory,
    rename_directory,
)
from ..permissions import has_read, has_write
from ..sources.sqlalchemy_dir import (
    fetch_dir_by_id,
    fetch_dirs_by_parent,
    save_directory,
    update_directory,
)
from ..sources.sqlalchemy_group import fetch_groups_by_user
from ..sources.sqlalchemy_permissions import fetch_permissions_for

dirs_router = APIRouter()


@dataclass(frozen=True, slots=True)
class CreateDirectoryRequest:
    name: str
    parent_id: str


@dirs_router.post("/directory", tags=["Directories"])
async def create_directory(body: CreateDirectoryRequest) -> Directory:
    d = mk_directory(body.name, body.parent_id).unwrap()
    save_directory(d)
    return d


@dataclass(frozen=True, slots=True)
class EditDirectoryReq:
    dir_id: str
    new_name: str
    new_parent_id: str


@dirs_router.patch("/directory", tags=["Directories"])
async def edit_directory(req: Request, body: EditDirectoryReq) -> Directory:
    session = req.state.session
    groups = fetch_groups_by_user(session.owner)
    group_names = [g.name for g in groups]

    d = fetch_dir_by_id(body.dir_id).unwrap_or_raise(BadRequest)

    prms = fetch_permissions_for([d.dir_id])
    prm = next((p for p in prms if p.item_id == d.dir_id), None)
    if not prm or not has_write(prm, session.owner, group_names):
        raise Forbidden("access denied")

    d = rename_directory(d, body.new_name).unwrap_or_raise(InternalServerError)
    d = change_directory_parent(d, body.new_parent_id).unwrap_or_raise(
        InternalServerError
    )

    return update_directory(d).unwrap_or_raise(BadRequest)


@dirs_router.get("/directories", tags=["Directories"])
async def read_dirs(
    req: Request, query: DirFilter = Depends()
) -> list[Directory | BrokenDirectory]:
    session = req.state.session

    groups = fetch_groups_by_user(session.owner)
    group_names = [g.name for g in groups]

    dirs = fetch_dirs_by_parent(query.parent_id)

    prms = fetch_permissions_for([d.dir_id for d in dirs])

    result: list[Directory | BrokenDirectory] = []
    for d in dirs:
        prm = next((p for p in prms if p.item_id == d.dir_id), None)
        if prm and has_read(prm, session.owner, group_names):
            result.append(d)
        else:
            result.append(BrokenDirectory(name=d.name, reason="access not allowed"))

    return result
