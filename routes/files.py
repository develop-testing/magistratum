from __future__ import annotations
from dataclasses import dataclass
from result import Ok, Err
from fastapi import APIRouter, Depends, Response

from .response import *
from files.text_file import (
    TextFileFilter,
    change_file_content,
    rename_file,
    new_file,
    destroy_file,
)
from files.sqlalchemy_file import (
    FetchFileError,
    SaveFileError,
    is_dir_exists,
    save_file,
    fetch_file_by_filter,
    fetch_file_by_name,
    delete_file_by_name,
    update_file,
)

files_router = APIRouter()


@dataclass(frozen=True, slots=True)
class FetchFileRequest:
    by_name: str = ""
    by_directory: str = ""
    limit: int = 10
    offset: int = 0


@files_router.get("/files", tags=["Files"])
async def read_files(query: FetchFileRequest = Depends()) -> Response:
    files = fetch_file_by_filter(
        TextFileFilter(query.by_name, query.by_directory, query.limit, query.offset)
    )
    return Success(files)


@dataclass(frozen=True, slots=True)
class CreateFileRequest:
    filename: str
    dirname: str
    content: str


@files_router.post("/file", tags=["Files"])
async def create_file(body: CreateFileRequest) -> Response:
    if body.dirname != "" and not is_dir_exists(body.dirname):
        return BadRequest("directory " + body.dirname + " not exists")

    result = new_file(body.filename, body.content).and_then(lambda fl: save_file(fl))

    match result:
        case Ok(file):
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


@files_router.patch("/file", tags=["Files"])
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


@files_router.delete("/file", tags=["Files"])
async def delete_file(file_name: str) -> Response:
    result = (
        fetch_file_by_name(file_name)
        .map(lambda fl: destroy_file(fl))
        .map(lambda fl: delete_file_by_name(fl.name))
    )

    match result:
        case Ok():
            return Success(True)
        case Err(FetchFileError() as err):
            return BadRequest(err.value)
        case _:
            return InternalServerError()
