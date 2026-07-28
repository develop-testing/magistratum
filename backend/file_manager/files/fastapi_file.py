from __future__ import annotations
import base64
import uuid
from dataclasses import dataclass
from pathlib import Path
from fastapi import APIRouter, Depends, Response, Request

from backend.router.response import *
from .files import *
from ..directories.sqlalchemy_dir import fetch_dir_by_id
from .sqlalchemy_file import (
    save_file,
    fetch_files_by_filter,
    fetch_rich_files_by_filter,
    fetch_file_by_id,
    delete_file_by_id,
    move_file,
    update_file_by_id,
    add_image_to_file,
)
from ..groups.sqlalchemy_group import fetch_groups_by_user
from ..permissions.permissions import Permissions, new_permissions, has_read, has_write

from ..permissions.sqlalchemy_permissions import (
    fetch_file_permissions_for,
    fetch_dir_permissions_for,
    save_file_permissions,
    update_file_permissions,
)

files_router = APIRouter()


def _value_to_perm_code(value: str) -> str:
    if value == "r":
        return "r-"
    if value == "w":
        return "-w"
    if value == "rw":
        return "rw"
    return "--"


ReadRet = list[TextFile | RichTextFile]


@files_router.get("/files", tags=["Files"])
async def read_files(req: Request, fltr: TextFileFilter = Depends()) -> ReadRet:
    session = req.state.session
    groups = fetch_groups_by_user(session.owner)
    group_names = [g.name for g in groups]

    files: list[TextFile] | list[RichTextFile]
    prms: list[Permissions]
    result: ReadRet = []

    match fltr.data_type:
        case "rich":
            files = fetch_rich_files_by_filter(fltr)
            prms = [f.perms for f in files]
        case _:
            files = fetch_files_by_filter(fltr)
            prms = fetch_file_permissions_for([id_of_file(f) for f in files])

    for file in files:
        prm = next((p for p in prms if p.item_id == id_of_file(file)), None)
        if prm and has_read(prm, session.owner, group_names):
            result.append(file)

    return result


@dataclass(frozen=True, slots=True)
class CreateFileRequest:
    filename: str
    dir_id: str
    content: str


@files_router.post("/file", tags=["Files"])
async def create_file(req: Request, body: CreateFileRequest) -> TextFile:
    username = req.state.session.owner

    parent_id: str | None = None
    if body.dir_id != "":
        dir = fetch_dir_by_id(body.dir_id)
        parent_id = dir.dir_id

        groups = fetch_groups_by_user(username)
        group_names = [g.name for g in groups]

        prms = fetch_dir_permissions_for([dir.dir_id])
        prm = next((p for p in prms if p.item_id == dir.dir_id), None)
        if not prm or not has_write(prm, username, group_names):
            raise Forbidden("access denied")

    fl = new_file(body.filename, body.content, parent_id)

    p = new_permissions(fl.file_id, username, "root", "rwr-")

    save_file(fl)
    save_file_permissions(p)

    return fl


@dataclass(frozen=True, slots=True)
class CopyFileRequest:
    file_id: str
    parent_id: str


@files_router.post("/file/copy", tags=["Files"])
async def copy_file(req: Request, body: CopyFileRequest) -> TextFile:
    username = req.state.session.owner
    groups = fetch_groups_by_user(username)
    group_names = [g.name for g in groups]

    fl = fetch_file_by_id(body.file_id)

    prms = fetch_file_permissions_for([fl.file_id])
    prm = next((p for p in prms if p.item_id == fl.file_id), None)
    if not prm or not has_read(prm, username, group_names):
        raise Forbidden("access denied")

    dir = fetch_dir_by_id(body.parent_id)

    dir_prms = fetch_dir_permissions_for([dir.dir_id])
    dir_prm = next((p for p in dir_prms if p.item_id == dir.dir_id), None)
    if not dir_prm or not has_write(dir_prm, username, group_names):
        raise Forbidden("access denied")

    new_fl = copy_file_to(fl, body.parent_id)

    p = new_permissions(new_fl.file_id, username, "root", "rwr-")

    save_file(new_fl)
    save_file_permissions(p)

    return new_fl


@dataclass(frozen=True, slots=True)
class EditFileRequest:
    file_id: str
    new_filename: str = ""
    new_content: str = ""
    new_parent_id: str = ""
    new_owner: str = ""
    new_group_name: str = ""
    new_group_perms: str = ""
    new_other_perms: str = ""
    new_cover: str = ""


@files_router.patch("/file", tags=["Files"])
async def edit_file(req: Request, body: EditFileRequest) -> TextFile:
    session = req.state.session
    groups = fetch_groups_by_user(session.owner)
    group_names = [g.name for g in groups]

    fl = fetch_file_by_id(body.file_id)

    prms = fetch_file_permissions_for([fl.file_id])
    prm = next((p for p in prms if p.item_id == fl.file_id), None)
    if not prm or not has_write(prm, session.owner, group_names):
        raise Forbidden("access denied")

    fl = change_file_content(fl, body.new_content)
    fl = rename_file(fl, body.new_filename)
    fl = change_file_parent(fl, body.new_parent_id)

    if body.new_parent_id:
        move_file(fl.file_id, body.new_parent_id)

    updated_fl = update_file_by_id(body.file_id, fl)

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
            else (prm.owner_name if prm else session.owner)
        )
        new_grp = (
            body.new_group_name
            if body.new_group_name
            else (prm.group_name if prm else "root")
        )
        updated_prm = new_permissions(body.file_id, new_owner, new_grp, new_content)
        update_file_permissions([updated_prm])

    if body.new_cover:
        _save_image(body.file_id, body.new_cover)

    return updated_fl


def _save_image(file_id: str, data_url: str) -> str:
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

    return add_image_to_file(file_id, f"/public/upload/{file_path.name}")


@dataclass(frozen=True, slots=True)
class DeletFileReq:
    file_id: str


@files_router.delete("/file", tags=["Files"])
async def delete_file(req: Request, body: DeletFileReq) -> bool:
    session = req.state.session
    groups = fetch_groups_by_user(session.owner)
    group_names = [g.name for g in groups]

    fl = fetch_file_by_id(body.file_id)

    prms = fetch_file_permissions_for([fl.file_id])
    prm = next((p for p in prms if p.item_id == fl.file_id), None)
    if not prm or not has_write(prm, session.owner, group_names):
        raise Forbidden("access denied")

    destroy_file(fl)

    return delete_file_by_id(fl.file_id)
