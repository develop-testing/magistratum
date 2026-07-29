from __future__ import annotations
import base64
import uuid
from dataclasses import dataclass
from pathlib import Path
from fastapi import APIRouter, Depends, Request

from sqlalchemy.engine import Connection

import backend.database.database as db

import backend.router.response as resp

from . import directory as dirs
from . import sqlalchemy_dir as dir_src
from ..permissions import permissions as prms

from ..groups import sqlalchemy_group as grps_src
from ..groups import groups as grps
from ..permissions import sqlalchemy_permissions as prms_src

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


CResult = dirs.Directory


@dirs_router.post("/directory", tags=["Directories"])
async def create_directory(req: Request, body: CreateDirectoryReq) -> CResult:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner
        permition = None

        if body.parent_id:
            group_names = grps.get_group_names(
                grps_src.fetch_groups_by_user(conn, session_owner)
            )
            parent_id = dir_src.fetch_dir_by_id(conn, body.parent_id).dir_id
            permitions = prms_src.fetch_dir_permissions_for(conn, [parent_id])

            permition = prms.find_permition_in_list(permitions, parent_id)
            if not permition or not prms.has_write(
                permition, session_owner, group_names
            ):
                raise resp.Forbidden("access denied")

        new_dir = dirs.new_directory(body.name, body.parent_id)
        group_name = permition.group_name if permition else "root"
        new_perm = prms.new_permissions(
            new_dir.dir_id,
            session_owner,
            group_name,
            "rw--",
        )

        conn = dir_src.save_directory(conn, new_dir)
        conn = prms_src.save_dir_permissions(conn, new_perm)
        conn.commit()

        return new_dir

    except dir_src.DirFetchError as e:
        raise resp.BadRequest(str(e))
    finally:
        conn.rollback()
        conn.close()


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
async def edit_directory(req: Request, body: EditDirectoryReq) -> dirs.Directory:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner
        groups = grps_src.fetch_groups_by_user(conn, session_owner)
        group_names = grps.get_group_names(groups)

        dir = dir_src.fetch_dir_by_id(conn, body.dir_id)

        permitions = prms_src.fetch_dir_permissions_for(conn, [dir.dir_id])
        prm = prms.find_permition_in_list(permitions, dir.dir_id)
        if not prm or not prms.has_write(prm, session_owner, group_names):
            raise resp.Forbidden("access denied")

        dir = dirs.rename_directory(dir, body.new_name)
        dir = dirs.change_directory_parent(dir, body.new_parent_id)

        conn = dir_src.update_directory(conn, dir)

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
            updated_prm = prms.new_permissions(
                body.dir_id, new_owner, new_grp, new_content
            )
            conn = prms_src.update_dir_permissions(conn, [updated_prm])

        if body.new_cover:
            _save_image(conn, body.dir_id, body.new_cover)

        conn.commit()

        return dir

    except dir_src.DirFetchError as e:
        raise resp.BadRequest(str(e))
    finally:
        conn.rollback()
        conn.close()


def _save_image(conn: Connection, dir_id: str, data_url: str) -> None:
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

    conn = dir_src.add_image_to_dir(conn, dir_id, f"/public/upload/{file_path.name}")


@dataclass(frozen=True, slots=True)
class DeleteDirectoryReq:
    dir_id: str


@dirs_router.delete("/directory", tags=["Directories"])
async def delete_dir(req: Request, body: DeleteDirectoryReq) -> bool:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner
        groups = grps_src.fetch_groups_by_user(conn, session_owner)
        group_names = grps.get_group_names(groups)

        dir = dir_src.fetch_dir_by_id(conn, body.dir_id)

        permitions = prms_src.fetch_dir_permissions_for(conn, [dir.dir_id])
        prm = prms.find_permition_in_list(permitions, dir.dir_id)
        if not prm or not prms.has_write(prm, session_owner, group_names):
            raise resp.Forbidden("access denied")

        conn = dir_src.delete_directory(conn, dir.dir_id)
        conn.commit()

        return True

    except dir_src.DirFetchError as e:
        raise resp.BadRequest(str(e))
    finally:
        conn.rollback()
        conn.close()


DirRdResult = list[dirs.Directory | dirs.RichDirectory | dirs.BrokenDirectory]


@dirs_router.get("/directories/root", tags=["Directories"])
async def read_root_dirs(req: Request) -> DirRdResult:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner

        groups = grps_src.fetch_groups_by_user(conn, session_owner)
        group_names = grps.get_group_names(groups)

        dir_list = dir_src.fetch_dirs_by_parent(conn, None)

        if not dir_list:
            raise resp.BadRequest("directories not found")

        permitions = prms_src.fetch_dir_permissions_for(
            conn, [d.dir_id for d in dir_list]
        )

        result: DirRdResult = []
        for d in dir_list:
            prm = prms.find_permition_in_list(permitions, d.dir_id)

            if prm and prms.has_read(prm, session_owner, group_names):
                image = dir_src.fetch_image_by_dir(conn, d.dir_id)
                result.append(
                    dirs.mk_rich_directory(
                        d,
                        prm,
                        image,
                    )
                )

        return result

    finally:
        conn.rollback()
        conn.close()


@dirs_router.get("/directories", tags=["Directories"])
async def read_dirs(req: Request, fltr: dirs.DirFilter = Depends()) -> DirRdResult:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner

        groups = grps_src.fetch_groups_by_user(conn, session_owner)
        group_names = grps.get_group_names(groups)

        dir_list: list[dirs.Directory] | list[dirs.RichDirectory]
        permitions: list[prms.Permissions]

        match fltr.data_type:
            case "rich":
                dir_list = dir_src.fetch_rich_dirs_by_filter(conn, fltr)
                permitions = [
                    d.perms for d in dir_list if isinstance(d, dirs.RichDirectory)
                ]
            case _:
                dir_list = dir_src.fetch_dirs_by_filter(conn, fltr)
                permitions = prms_src.fetch_dir_permissions_for(
                    conn,
                    [d.dir_id for d in dir_list if isinstance(d, dirs.Directory)],
                )

        result: DirRdResult = []
        for d in dir_list:
            d_id = d.dir_id if isinstance(d, dirs.Directory) else d.directory.dir_id
            prm = prms.find_permition_in_list(permitions, d_id)

            if prm and prms.has_read(prm, session_owner, group_names):
                if fltr.only_can_write and not prms.has_write(
                    prm, session_owner, group_names
                ):
                    continue
                result.append(d)

        return result

    finally:
        conn.rollback()
        conn.close()
