from __future__ import annotations
import base64
import uuid
from dataclasses import dataclass
from pathlib import Path
from fastapi import APIRouter, Depends, Request

from backend.router.response import *

from .directory import *

from ..permissions.permissions import (
    Permissions,
    has_read,
    has_write,
    new_permissions,
)
from .sqlalchemy_dir import *
from .sqlalchemy_dir import (
    add_image_to_dir,
    fetch_image_by_dir,
    fetch_rich_dirs_by_filter,
)
from ..groups.sqlalchemy_group import fetch_groups_by_user
from ..permissions.sqlalchemy_permissions import (
    fetch_permissions_for,
    save_permissions,
    update_permissions,
)

dirs_router = APIRouter()


def _value_to_perm_code(value: str) -> str:
    if value == "r":
        return "r-"
    if value == "w":
        return "-w"
    if value == "rw":
        return "rw"
    return "--"


@dataclass(frozen=True, slots=True)
class CreateDirectoryReq:
    name: str
    parent_id: str


@dirs_router.post("/directory", tags=["Directories"])
async def create_directory(req: Request, body: CreateDirectoryReq) -> Directory:
    try:

        session_owner = req.state.session.owner
        group_name = ""

        if body.parent_id:
            groups = fetch_groups_by_user(session_owner)
            group_names = [g.name for g in groups]

            parent_dir = fetch_dir_by_id(body.parent_id)

            prms = fetch_permissions_for([parent_dir.dir_id])
            prm = next((p for p in prms if p.item_id == parent_dir.dir_id), None)
            if not prm or not has_write(prm, session_owner, group_names):
                raise Forbidden("access denied")

            group_name = prm.group_name

        new_dir = new_directory(body.name, body.parent_id)
        new_perm = new_permissions(new_dir.dir_id, session_owner, group_name, "rw--")

        new_dir = save_directory(new_dir)
        new_perm = save_permissions(new_perm)

        return new_dir

    except DirFetchError as e:
        raise BadRequest(str(e))


@dataclass(frozen=True, slots=True)
class EditDirectoryReq:
    dir_id: str
    new_name: str = ""
    new_parent_id: str = ""
    new_owner: str = ""
    new_group_name: str = ""
    new_group_perms: str = ""
    new_other_perms: str = ""
    new_cover: str = ""


@dirs_router.patch("/directory", tags=["Directories"])
async def edit_directory(req: Request, body: EditDirectoryReq) -> Directory:
    try:

        session_owner = req.state.session.owner
        groups = fetch_groups_by_user(session_owner)
        group_names = [g.name for g in groups]

        dir = fetch_dir_by_id(body.dir_id)

        prms = fetch_permissions_for([dir.dir_id])
        prm = next((p for p in prms if p.item_id == dir.dir_id), None)
        if not prm or not has_write(prm, session_owner, group_names):
            raise Forbidden("access denied")

        dir = rename_directory(dir, body.new_name)
        dir = change_directory_parent(dir, body.new_parent_id)

        updated_dir = update_directory(dir)

        if (
            body.new_group_perms
            or body.new_other_perms
            or body.new_owner
            or body.new_group_name
        ):
            group_part = (
                _value_to_perm_code(body.new_group_perms)
                if body.new_group_perms
                else (prm.content[0:2] if prm else "--")
            )
            other_part = (
                _value_to_perm_code(body.new_other_perms)
                if body.new_other_perms
                else (prm.content[2:4] if prm else "--")
            )
            new_content = group_part + other_part
            new_owner = (
                body.new_owner
                if body.new_owner
                else (prm.owner_name if prm else session_owner)
            )
            new_grp = (
                body.new_group_name
                if body.new_group_name
                else (prm.group_name if prm else "root")
            )
            updated_prm = new_permissions(body.dir_id, new_owner, new_grp, new_content)
            update_permissions([updated_prm])

        if body.new_cover:
            _save_image(body.dir_id, body.new_cover)

        return updated_dir

    except DirFetchError as e:
        raise BadRequest(str(e))


def _save_image(dir_id: str, data_url: str) -> str:
    if "," not in data_url:
        raise ValueError("invalid image data")

    header, encoded = data_url.split(",", 1)
    ext = "png"
    if "jpeg" in header or "jpg" in header:
        ext = "jpg"
    elif "gif" in header:
        ext = "gif"
    elif "webp" in header:
        ext = "webp"

    try:
        raw = base64.b64decode(encoded)
    except Exception:
        raise ValueError("invalid base64 data")

    images_dir = Path("frontend/public/upload")
    images_dir.mkdir(parents=True, exist_ok=True)

    file_path = images_dir / f"{uuid.uuid4().hex}.{ext}"
    file_path.write_bytes(raw)

    return add_image_to_dir(dir_id, f"/public/upload/{file_path.name}")


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
        prm = next((p for p in prms if p.item_id == dir.dir_id), None)
        if not prm or not has_write(prm, session_owner, group_names):
            raise Forbidden("access denied")

        return delete_directory(dir.dir_id)

    except DirFetchError as e:
        raise BadRequest(str(e))


DirRdResult = list[Directory | RichDirectory | BrokenDirectory]


@dirs_router.get("/directories/root", tags=["Directories"])
async def read_root_dirs(req: Request) -> DirRdResult:
    session_owner = req.state.session.owner

    groups = fetch_groups_by_user(session_owner)
    group_names = [g.name for g in groups]

    dirs = fetch_dirs_by_parent("")

    if not dirs:
        raise BadRequest("directories not found")

    prms = fetch_permissions_for([d.dir_id for d in dirs])

    result: DirRdResult = []
    for d in dirs:
        prm = next((p for p in prms if p.item_id == d.dir_id), None)

        if prm and has_read(prm, session_owner, group_names):
            image = fetch_image_by_dir(d.dir_id)
            result.append(
                mk_rich_directory(
                    d,
                    prm,
                    image,
                )
            )

    return result


@dirs_router.get("/directories", tags=["Directories"])
async def read_dirs(req: Request, fltr: DirFilter = Depends()) -> DirRdResult:
    session_owner = req.state.session.owner

    groups = fetch_groups_by_user(session_owner)
    group_names = [g.name for g in groups]

    dirs: list[Directory] | list[RichDirectory]
    prms: list[Permissions]

    match fltr.data_type:
        case "rich":
            dirs = fetch_rich_dirs_by_filter(fltr)
            prms = [d.perms for d in dirs if isinstance(d, RichDirectory)]
        case _:
            dirs = fetch_dirs_by_filter(fltr)
            prms = fetch_permissions_for(
                [d.dir_id for d in dirs if isinstance(d, Directory)]
            )

    result: DirRdResult = []
    for d in dirs:
        d_id = d.dir_id if isinstance(d, Directory) else d.directory.dir_id
        prm = next((p for p in prms if p.item_id == d_id), None)

        if prm and has_read(prm, session_owner, group_names):
            result.append(d)

    return result
