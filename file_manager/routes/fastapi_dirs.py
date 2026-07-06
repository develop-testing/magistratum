from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter, Depends, Request

from ..directory import BrokenDirectory, DirFilter, Directory, mk_directory
from ..permissions import has_read
from ..sources.sqlalchemy_dir import fetch_dirs_by_parent, save_directory
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
