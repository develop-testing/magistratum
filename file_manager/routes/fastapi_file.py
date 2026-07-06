from __future__ import annotations
from dataclasses import dataclass
from result import Result, Ok, Err
from fastapi import APIRouter, Depends, Response, Request

from router.response import *
from ..files import (
    TextFileFilter,
    TextFile,
    BrokenFile,
    change_file_content,
    rename_file,
    new_file,
    destroy_file,
)
from ..sources.sqlalchemy_dir import fetch_dir_by_name
from ..sources.sqlalchemy_file import (
    save_file,
    fetch_file_by_filter,
    fetch_file_by_name,
    delete_file_by_id,
    update_file,
)
from ..sources.sqlalchemy_group import fetch_groups_by_user
from ..permissions import Permissions, new_permissions, has_read, has_write

from ..sources.sqlalchemy_permissions import fetch_permissions_for

files_router = APIRouter()


@dataclass(frozen=True, slots=True)
class FetchFileReq:
    by_name: str = ""
    by_directory: str = ""
    limit: int = 10
    offset: int = 0


ReadRet = list[TextFile | BrokenFile]


@files_router.get("/files", tags=["Files"])
async def read_files(req: Request, query: FetchFileReq = Depends()) -> ReadRet:
    session = req.state.session

    groups = fetch_groups_by_user(session.owner)

    files = fetch_file_by_filter(
        TextFileFilter(query.by_name, query.by_directory, query.limit, query.offset)
    )

    prms = fetch_permissions_for([file.file_id for file in files])

    group_names = [g.name for g in groups]

    result: list[TextFile | BrokenFile] = []
    for f in files:
        prm = next((p for p in prms if p.item_id == f.file_id), None)
        if prm and has_read(prm, session.owner, group_names):
            result.append(f)
        else:
            result.append(BrokenFile(name=f.name, reason="access not allowed"))

    return result


@dataclass(frozen=True, slots=True)
class CreateFileRequest:
    filename: str
    dirname: str
    content: str


@files_router.post("/file", tags=["Files"])
async def create_file(req: Request, body: CreateFileRequest) -> TextFile:
    username = req.state.session.owner

    if body.dirname != "":
        dir = fetch_dir_by_name(body.dirname).unwrap_or_raise(BadRequest)

        groups = fetch_groups_by_user(username)
        group_names = [g.name for g in groups]

        prms = fetch_permissions_for([dir.dir_id])
        prm = next((p for p in prms if p.item_id == dir.dir_id), None)
        if not prm or not has_write(prm, username, group_names):
            raise Forbidden("access denied")

    fl = new_file(body.filename, body.content).unwrap_or_raise(InternalServerError)

    p = new_permissions(fl.file_id, username, "root", "rwr-").unwrap_or_raise(
        InternalServerError
    )

    return save_file(fl, p).unwrap_or_raise(BadRequest)


@dataclass(frozen=True, slots=True)
class EditFileRequest:
    filename: str
    new_filename: str
    new_content: str


@files_router.patch("/file", tags=["Files"])
async def edit_file(req: Request, body: EditFileRequest) -> TextFile:
    session = req.state.session
    groups = fetch_groups_by_user(session.owner)
    group_names = [g.name for g in groups]

    fl = fetch_file_by_name(body.filename).unwrap_or_raise(BadRequest)

    prms = fetch_permissions_for([fl.file_id])
    prm = next((p for p in prms if p.item_id == fl.file_id), None)
    if not prm or not has_write(prm, session.owner, group_names):
        raise Forbidden("access denied")

    fl = change_file_content(fl, body.new_content).unwrap_or_raise(InternalServerError)
    fl = rename_file(fl, body.new_filename).unwrap_or_raise(InternalServerError)

    return update_file(body.filename, fl).unwrap_or_raise(BadRequest)


@files_router.delete("/file", tags=["Files"])
async def delete_file(req: Request, file_name: str) -> bool:
    session = req.state.session
    groups = fetch_groups_by_user(session.owner)
    group_names = [g.name for g in groups]

    fl = fetch_file_by_name(file_name).unwrap_or_raise(BadRequest)

    prms = fetch_permissions_for([fl.file_id])
    prm = next((p for p in prms if p.item_id == fl.file_id), None)
    if not prm or not has_write(prm, session.owner, group_names):
        raise Forbidden("access denied")

    destroy_file(fl)

    return delete_file_by_id(fl.file_id)
