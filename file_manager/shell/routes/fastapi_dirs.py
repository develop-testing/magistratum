from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter, Depends, Request

from router.response import *

from ...directories.directory import *

from ...permissions import has_read, has_write, new_permissions, Permissions
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

PList = list[Permissions]


def only_read_permitions(prms: PList, uname: str, groups: list[str]) -> PList:
    result: PList = []

    for prm in prms:
        if has_read(prm, uname, groups):
            result = [*result, prm]

    return result


def only_write_permitions(prms: PList, uname: str, groups: list[str]) -> PList:
    result: PList = []

    for prm in prms:
        if has_write(prm, uname, groups):
            result = [*result, prm]

    return result


DrsFltrRes = list[Directory | BrokenDirectory]


def filter_dirs_by_perms(dirs: list[Directory], prms: list[Permissions]) -> DrsFltrRes:
    result: DrsFltrRes = []

    for dir in dirs:
        prm = next((p for p in prms if p.item_id == dir.dir_id), None)

        if not prm:
            result = [*result, mk_broken_directory(dir.name, "access not allowed")]
            continue

        result = [*result, dir]

    return result


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

    parent_dir = fetch_dir_by_id(body.parent_id)

    if not parent_dir:
        raise BadRequest("directories not found")

    prm = fetch_permissions_for([parent_dir.dir_id])[0]

    if not prm or not has_write(prm, session_owner, group_names):
        raise Forbidden("access denied")

    new_dir = mk_directory(body.name, body.parent_id)
    new_perm = new_permissions(new_dir.dir_id, session_owner, prm.group_name, "rwr-")

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

    d = fetch_dir_by_id(body.dir_id)

    prms = fetch_permissions_for([d.dir_id])
    prm = next((p for p in prms if p.item_id == d.dir_id), None)
    if not prm or not has_write(prm, session.owner, group_names):
        raise Forbidden("access denied")

    d = rename_directory(d, body.new_name)
    d = change_directory_parent(d, body.new_parent_id)

    return update_directory(d)


@dataclass(frozen=True, slots=True)
class DeleteDirectoryReq:
    dir_id: str


@dirs_router.delete("/directory", tags=["Directories"])
async def delete_dir(req: Request, body: DeleteDirectoryReq) -> bool:
    session = req.state.session
    groups = fetch_groups_by_user(session.owner)
    group_names = [g.name for g in groups]

    d = fetch_dir_by_id(body.dir_id)

    prms = fetch_permissions_for([d.dir_id])
    prm = next((p for p in prms if p.item_id == d.dir_id), None)
    if not prm or not has_write(prm, session.owner, group_names):
        raise Forbidden("access denied")

    destroy_directory(d)
    return delete_directory(d.dir_id)


RdDirsRslt = list[Directory | BrokenDirectory]


@dirs_router.get("/directories", tags=["Directories"])
async def read_dirs(req: Request, fltr: DirFilter = Depends()) -> RdDirsRslt:
    session_owner = req.state.session.owner

    groups = fetch_groups_by_user(session_owner)
    group_names = [g.name for g in groups]

    dirs = fetch_dirs_by_parent(fltr.parent_id)

    if not dirs:
        return []

    prms = fetch_permissions_for([d.dir_id for d in dirs])

    if fltr.only_can_read:
        prms = only_read_permitions(prms, session_owner, group_names)

    if fltr.only_can_write:
        prms = only_write_permitions(prms, session_owner, group_names)

    result = filter_dirs_by_perms(dirs, prms)

    return result
