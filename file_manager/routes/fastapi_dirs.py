from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter

from ..directory import Directory, mk_directory
from ..sources.sqlalchemy_dir import save_directory

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
