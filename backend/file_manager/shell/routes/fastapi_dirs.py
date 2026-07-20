from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter, Depends, Request

from backend.router.response import *

from ...directories.directory import *

from ...permissions import has_read, has_write, new_permissions, Permissions
from ..sources.sqlalchemy_dir import *
from ..sources.sqlalchemy_dir import fetch_image_by_dir, fetch_rich_dirs_by_filter
from ..sources.sqlalchemy_group import fetch_groups_by_user
from ..sources.sqlalchemy_permissions import fetch_permissions_for, save_permissions

dirs_router = APIRouter()


@dataclass(frozen=True, slots=True)
class CreateDirectoryReq:
    name: str
    parent_id: str


@dirs_router.post("/directory", tags=["Directories"])
async def create_directory(req: Request, body: CreateDirectoryReq) -> Directory:
    try:

        session_owner = req.state.session.owner

        groups = fetch_groups_by_user(session_owner)
        group_names = [g.name for g in groups]

        parent_dir = fetch_dir_by_id(body.parent_id)

        prm = fetch_permissions_for([parent_dir.dir_id])
        prm = only_write_permitions(prm, session_owner, group_names)
        access_granted = check_dir_has_perms(parent_dir, prm)

        if not access_granted:
            raise Forbidden("access denied")

        new_dir = new_directory(body.name, body.parent_id)
        new_perm = new_permissions(
            new_dir.dir_id, session_owner, prm[0].group_name, "rwr-"
        )

        new_dir = save_directory(new_dir)
        new_perm = save_permissions(new_perm)

        return new_dir

    except DirFetchError as e:
        raise BadRequest(str(e))


@dataclass(frozen=True, slots=True)
class EditDirectoryReq:
    dir_id: str
    new_name: str
    new_parent_id: str


@dirs_router.patch("/directory", tags=["Directories"])
async def edit_directory(req: Request, body: EditDirectoryReq) -> Directory:
    try:

        session_owner = req.state.session.owner
        groups = fetch_groups_by_user(session_owner)
        group_names = [g.name for g in groups]

        dir = fetch_dir_by_id(body.dir_id)

        prms = fetch_permissions_for([dir.dir_id])
        prms = only_write_permitions(prms, session_owner, group_names)
        access_granted = check_dir_has_perms(dir, prms)

        if not access_granted:
            raise Forbidden("access denied")

        dir = rename_directory(dir, body.new_name)
        dir = change_directory_parent(dir, body.new_parent_id)

        return update_directory(dir)

    except DirFetchError as e:
        raise BadRequest(str(e))


@dataclass(frozen=True, slots=True)
class DeleteDirectoryReq:
    dir_id: str


# TODO добавить каскадное удаление файлов и картинок и другое
@dirs_router.delete("/directory", tags=["Directories"])
async def delete_dir(req: Request, body: DeleteDirectoryReq) -> bool:
    try:

        session_owner = req.state.session.owner
        groups = fetch_groups_by_user(session_owner)
        group_names = [g.name for g in groups]

        dir = fetch_dir_by_id(body.dir_id)

        prms = fetch_permissions_for([dir.dir_id])
        prms = only_write_permitions(prms, session_owner, group_names)
        access_granted = check_dir_has_perms(dir, prms)

        if not access_granted:
            raise Forbidden("access denied")

        return delete_directory(dir.dir_id)

    except DirFetchError as e:
        raise BadRequest(str(e))


DirRdResult = list[Directory | RichDirectory | BrokenDirectory]


@dirs_router.get("/directories", tags=["Directories"])
async def read_dirs(req: Request, fltr: DirFilter = Depends()) -> DirRdResult:
    session_owner = req.state.session.owner

    groups = fetch_groups_by_user(session_owner)
    group_names = [g.name for g in groups]

    dirs: list[Directory | RichDirectory]
    match (fltr.data_type):
        case "rich":
            dirs = [*fetch_rich_dirs_by_filter(fltr)]
        case _:
            dirs = [*fetch_dirs_by_filter(fltr)]

    if not dirs:
        raise BadRequest("directories not found")

    prms = fetch_permissions_for(
        [d.dir_id if isinstance(d, Directory) else d.directory.dir_id for d in dirs]
    )

    result: DirRdResult = []
    for d in dirs:
        d_id = d.dir_id if isinstance(d, Directory) else d.directory.dir_id
        prm = next((p for p in prms if p.item_id == d_id), None)
        if not prm or not has_read(prm, session_owner, group_names):
            name = d.name if isinstance(d, Directory) else d.directory.name
            result.append(BrokenDirectory(name=name, reason="access not allowed"))
            continue
        result.append(d)

    return result


PList = list[Permissions]


def only_write_permitions(prms: PList, uname: str, groups: list[str]) -> PList:
    result: PList = []

    for prm in prms:
        if has_write(prm, uname, groups):
            result = [*result, prm]

    return result
