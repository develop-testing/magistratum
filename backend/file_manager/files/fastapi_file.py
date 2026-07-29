from __future__ import annotations
import base64
import uuid
from dataclasses import dataclass
from pathlib import Path
from fastapi import APIRouter, Depends, Response, Request

from sqlalchemy.engine import Connection

import backend.database.database as db
import backend.router.response as resp
from . import files as files_ent, sqlalchemy_file as file_src
from ..directories import sqlalchemy_dir as dir_src
from ..groups import groups as grps, sqlalchemy_group as grps_src
from ..permissions import permissions as prms, sqlalchemy_permissions as prms_src

files_router = APIRouter()


def _value_to_perm_code(value: str) -> str:
    if value == "r":
        return "r-"
    if value == "w":
        return "-w"
    if value == "rw":
        return "rw"
    return "--"


ReadRet = list[files_ent.TextFile | files_ent.RichTextFile]


@files_router.get("/files", tags=["Files"])
async def read_files(
    req: Request, fltr: files_ent.TextFileFilter = Depends()
) -> ReadRet:
    conn = db.engine.connect()
    try:
        session = req.state.session
        groups = grps_src.fetch_groups_by_user(conn, session.owner)
        group_names = grps.get_group_names(groups)

        files: list[files_ent.TextFile] | list[files_ent.RichTextFile]
        permitions: list[prms.Permissions]
        result: ReadRet = []

        match fltr.data_type:
            case "rich":
                files = file_src.fetch_rich_files_by_filter(conn, fltr)
                permitions = [f.perms for f in files]
            case _:
                files = file_src.fetch_files_by_filter(conn, fltr)
                permitions = prms_src.fetch_file_permissions_for(
                    conn, [files_ent.id_of_file(f) for f in files]
                )

        for file in files:
            prm = prms.find_permition_in_list(permitions, files_ent.id_of_file(file))
            if prm and prms.has_read(prm, session.owner, group_names):
                result.append(file)

        return result

    finally:
        conn.rollback()
        conn.close()


@dataclass(frozen=True, slots=True)
class CreateFileRequest:
    filename: str
    dir_id: str
    content: str


@files_router.post("/file", tags=["Files"])
async def create_file(req: Request, body: CreateFileRequest) -> files_ent.TextFile:
    conn = db.engine.connect()
    try:
        username = req.state.session.owner

        parent_id: str | None = None
        if body.dir_id != "":
            dir = dir_src.fetch_dir_by_id(conn, body.dir_id)
            parent_id = dir.dir_id

            groups = grps_src.fetch_groups_by_user(conn, username)
            group_names = grps.get_group_names(groups)

            permitions = prms_src.fetch_dir_permissions_for(conn, [dir.dir_id])
            prm = prms.find_permition_in_list(permitions, dir.dir_id)
            if not prm or not prms.has_write(prm, username, group_names):
                raise resp.Forbidden("access denied")

        fl = files_ent.new_file(body.filename, body.content, parent_id)

        p = prms.new_permissions(fl.file_id, username, "root", "rwr-")

        conn = file_src.save_file(conn, fl)
        conn = prms_src.save_file_permissions(conn, p)
        conn.commit()

        return fl

    finally:
        conn.rollback()
        conn.close()


@dataclass(frozen=True, slots=True)
class CopyFileRequest:
    file_id: str
    parent_id: str


@files_router.post("/file/copy", tags=["Files"])
async def copy_file(req: Request, body: CopyFileRequest) -> files_ent.TextFile:
    conn = db.engine.connect()
    try:
        username = req.state.session.owner
        groups = grps_src.fetch_groups_by_user(conn, username)
        group_names = grps.get_group_names(groups)

        fl = file_src.fetch_file_by_id(conn, body.file_id)

        permitions = prms_src.fetch_file_permissions_for(conn, [fl.file_id])
        prm = prms.find_permition_in_list(permitions, fl.file_id)
        if not prm or not prms.has_read(prm, username, group_names):
            raise resp.Forbidden("access denied")

        dir = dir_src.fetch_dir_by_id(conn, body.parent_id)

        dir_permitions = prms_src.fetch_dir_permissions_for(conn, [dir.dir_id])
        dir_prm = prms.find_permition_in_list(dir_permitions, dir.dir_id)
        if not dir_prm or not prms.has_write(dir_prm, username, group_names):
            raise resp.Forbidden("access denied")

        new_fl = files_ent.copy_file_to(fl, body.parent_id)

        p = prms.new_permissions(new_fl.file_id, username, "root", "rwr-")

        conn = file_src.save_file(conn, new_fl)
        conn = prms_src.save_file_permissions(conn, p)
        conn.commit()

        return new_fl

    finally:
        conn.rollback()
        conn.close()


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
async def edit_file(req: Request, body: EditFileRequest) -> files_ent.TextFile:
    conn = db.engine.connect()
    try:
        session = req.state.session
        groups = grps_src.fetch_groups_by_user(conn, session.owner)
        group_names = grps.get_group_names(groups)

        fl = file_src.fetch_file_by_id(conn, body.file_id)

        permitions = prms_src.fetch_file_permissions_for(conn, [fl.file_id])
        prm = prms.find_permition_in_list(permitions, fl.file_id)
        if not prm or not prms.has_write(prm, session.owner, group_names):
            raise resp.Forbidden("access denied")

        fl = files_ent.change_file_content(fl, body.new_content)
        fl = files_ent.rename_file(fl, body.new_filename)
        fl = files_ent.change_file_parent(fl, body.new_parent_id)

        if body.new_parent_id:
            conn = file_src.move_file(conn, fl.file_id, body.new_parent_id)

        conn = file_src.update_file_by_id(conn, body.file_id, fl)

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
            updated_prm = prms.new_permissions(
                body.file_id, new_owner, new_grp, new_content
            )
            conn = prms_src.update_file_permissions(conn, [updated_prm])

        if body.new_cover:
            _save_image(conn, body.file_id, body.new_cover)

        conn.commit()

        return fl

    finally:
        conn.rollback()
        conn.close()


def _save_image(conn: Connection, file_id: str, data_url: str) -> None:
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

    conn = file_src.add_image_to_file(conn, file_id, f"/public/upload/{file_path.name}")


@dataclass(frozen=True, slots=True)
class DeletFileReq:
    file_id: str


@files_router.delete("/file", tags=["Files"])
async def delete_file(req: Request, body: DeletFileReq) -> bool:
    conn = db.engine.connect()
    try:
        session = req.state.session
        groups = grps_src.fetch_groups_by_user(conn, session.owner)
        group_names = grps.get_group_names(groups)

        fl = file_src.fetch_file_by_id(conn, body.file_id)

        permitions = prms_src.fetch_file_permissions_for(conn, [fl.file_id])
        prm = prms.find_permition_in_list(permitions, fl.file_id)
        if not prm or not prms.has_write(prm, session.owner, group_names):
            raise resp.Forbidden("access denied")

        files_ent.destroy_file(fl)

        conn = file_src.delete_file_by_id(conn, fl.file_id)
        conn.commit()

        return True

    finally:
        conn.rollback()
        conn.close()
