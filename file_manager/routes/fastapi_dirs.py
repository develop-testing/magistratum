from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter, Depends, Request

from router.response import *

from ..directory import (
    BrokenDirectory,
    DirFilter,
    Directory,
    change_directory_parent,
    destroy_directory,
    mk_directory,
    rename_directory,
)
from ..files import BrokenFile, TextFile, TextFileFilter
from ..permissions import has_read, has_write, new_permissions
from ..sources.sqlalchemy_dir import (
    delete_directory,
    fetch_dir_by_id,
    fetch_dirs_by_parent,
    save_directory,
    update_directory,
    fetch_dir_by_name,
)
from ..sources.sqlalchemy_group import fetch_groups_by_user
from ..sources.sqlalchemy_permissions import fetch_permissions_for, save_permissions
from ..sources.sqlalchemy_file import fetch_file_by_filter

dirs_router = APIRouter()


@dataclass(frozen=True, slots=True)
class CreateDirectoryRequest:
    name: str
    parent_id: str


@dirs_router.post("/directory", tags=["Directories"])
async def create_directory(req: Request, body: CreateDirectoryRequest) -> Directory:
    session_owner = req.state.session.owner

    groups = fetch_groups_by_user(session_owner)
    group_names = [g.name for g in groups]

    parent_dir = fetch_dir_by_id(body.parent_id).unwrap_or_raise(BadRequest)

    if not parent_dir:
        raise BadRequest("directories not found")

    prm = fetch_permissions_for([parent_dir.dir_id])[0]

    if not prm or not has_write(prm, session_owner, group_names):
        raise Forbidden("access denied")

    new_dir = mk_directory(body.name, body.parent_id).unwrap_or_raise(BadRequest)
    new_perm = new_permissions(
        new_dir.dir_id, session_owner, prm.group_name, "rwr-"
    ).unwrap_or_raise(BadRequest)

    new_dir = save_directory(new_dir)
    new_perm = save_permissions(new_perm)

    return new_dir


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


@dirs_router.delete("/directory", tags=["Directories"])
async def delete_dir(req: Request, dir_id: str) -> bool:
    session = req.state.session
    groups = fetch_groups_by_user(session.owner)
    group_names = [g.name for g in groups]

    d = fetch_dir_by_id(dir_id).unwrap_or_raise(BadRequest)

    prms = fetch_permissions_for([d.dir_id])
    prm = next((p for p in prms if p.item_id == d.dir_id), None)
    if not prm or not has_write(prm, session.owner, group_names):
        raise Forbidden("access denied")

    destroy_directory(d)
    return delete_directory(d.dir_id)


@dirs_router.get("/directories", tags=["Directories"])
async def read_dirs(
    req: Request, query: DirFilter = Depends()
) -> list[Directory | BrokenDirectory]:
    session_owner = req.state.session.owner

    groups = fetch_groups_by_user(session_owner)
    group_names = [g.name for g in groups]

    dirs = fetch_dirs_by_parent(query.parent_id)

    if not dirs:
        return []

    prms = fetch_permissions_for([d.dir_id for d in dirs])

    if not prms:
        raise BadRequest("invalid directorises")

    result: list[Directory | BrokenDirectory] = []
    for d in dirs:
        prm = next((p for p in prms if p.item_id == d.dir_id), None)

        if not prm or not has_read(prm, session_owner, group_names):
            result.append(BrokenDirectory(name=d.name, reason="access not allowed"))
            continue

        result.append(d)

    return result


@dataclass(frozen=True, slots=True)
class DirectoryItem:
    item_id: str
    type: str
    img: str
    name: str
    owner: str
    group: str

@dataclass(frozen=True, slots=True)
class BrokenItem:
    name: str
    reason: str

Result = list[DirectoryItem | BrokenItem]

@dirs_router.get("/directory/content", tags=["Directories"])
async def directory_content(req: Request, dir_id: str) -> Result:
    session_owner = req.state.session.owner

    groups = fetch_groups_by_user(session_owner)
    group_names = [g.name for g in groups]

    dirs = fetch_dirs_by_parent(dir_id)

    files = fetch_file_by_filter(TextFileFilter("", dir_id, 0, 0))

    prms = fetch_permissions_for([d.dir_id for d in dirs] + [f.file_id for f in files])

    result: Result = []

    for d in dirs:
        prm = next((p for p in prms if p.item_id == d.dir_id), None)

        if not prm or not has_read(prm, session_owner, group_names):
            result += [BrokenItem(name=d.name, reason="access not allowed")]
            continue
        
        result += [
            DirectoryItem(
                type="dir",
                item_id=d.dir_id,
                img="https://warhammergames.ru/_pu/3/s42932075.jpg",
                name=d.name,
                owner=prm.owner_name,
                group=prm.group_name,
            )
        ]

    for f in files:
        prm = next((p for p in prms if p.item_id == f.file_id), None)

        if not prm or not has_read(prm, session_owner, group_names):
            result += [BrokenFile(name=f.name, reason="access not allowed")]
            continue

        result += [
            DirectoryItem(
                type="text_file",
                item_id=d.dir_id,
                img="https://warhammergames.ru/_pu/3/s42932075.jpg",
                name=d.name,
                owner=prm.owner_name,
                group=prm.group_name,
            )
        ]

    return result
