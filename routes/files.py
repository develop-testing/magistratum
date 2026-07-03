from __future__ import annotations
from dataclasses import dataclass
from result import Ok, Err, Result, is_err
from fastapi import APIRouter, Request, Response

from .response import *
from files.file import change_file_content, rename_file, FileFilter
from files.sqlalchemy_file import *

files_router = APIRouter()


@dataclass(frozen=True, slots=True)
class CreateFileRequest:
    filename: str
    dirname: str
    content: str


@files_router.post("/files/create", tags=["Files"])
async def create_file(body: CreateFileRequest) -> Response:
    if body.dirname != "" and not is_dir_exists(body.dirname):
        return BadRequest("directory " + body.dirname + " not exists")

    result = new_file(body.filename, body.content).and_then(lambda fl: save_file(fl))

    match result:
        case Ok(file):
            print(file)
            return Success(file)
        case Err(SaveFileError() as err):
            return BadRequest(err.value)
        case _:
            return InternalServerError()


@dataclass(frozen=True, slots=True)
class EditFileRequest:
    filename: str
    new_filename: str
    new_content: str


@files_router.put("/files/edit", tags=["Files"])
async def edit_file(body: EditFileRequest) -> Response:
    result = (
        fetch_file_by_name(body.filename)
        .and_then(lambda fl: change_file_content(fl, body.new_content))
        .and_then(lambda fl: rename_file(fl, body.new_filename))
        .and_then(lambda fl: update_file(body.filename, fl))
    )

    match result:
        case Ok(file):
            return Success(file)
        case Err(SaveFileError() as err):
            return BadRequest(err.value)
        case Err(FetchFileError() as err):
            return BadRequest(err.value)
        case _:
            return InternalServerError()


@dataclass(frozen=True, slots=True)
class FetchFileRequest:
    by_name: str
    by_directory: str
    limit: int = 10
    offset: int = 0


@files_router.post("/files/read", tags=["Files"])
async def read_files(body: FetchFileRequest) -> Response:
    files = fetch_file_by_filter(
        FileFilter(body.by_name, body.by_directory, body.limit, body.offset)
    )
    return Success(files)
