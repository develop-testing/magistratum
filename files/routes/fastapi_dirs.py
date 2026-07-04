from __future__ import annotations
from dataclasses import dataclass
from result import Ok
from fastapi import APIRouter, Depends, Response

from router.response import *
from ..sources.sqlalchemy_dir import is_dir_exists, save_directory
from ..directory import mk_directory

dirs_router = APIRouter()


@dataclass(frozen=True, slots=True)
class CreateDirectoryRequest:
    name: str
    parent_id: str


@dirs_router.post("/directory", tags=["Directories"])
async def create_directory(body: CreateDirectoryRequest) -> Response:
    dir = mk_directory(body.name, body.parent_id).map(lambda dir: save_directory(dir))

    match dir:
        case Ok(d):
            return Success(d)
        case _:
            return InternalServerError()
