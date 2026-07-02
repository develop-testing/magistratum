from __future__ import annotations
from dataclasses import dataclass
from result import Ok, Err, Result
from fastapi import APIRouter, Request, Response

from .response import *
from files.file import change_file_content, rename_file
from files.sqlalchemy_file import *

files_router = APIRouter()


@dataclass(frozen=True, slots=True)
class CreateFileRequest:
    filename: str
    dirname: str
    content: str


@files_router.post("/files/create", tags=["Files"])
async def create_file(body: CreateFileRequest) -> Response:
    try:
        if body.dirname != "" and not is_dir_exists(body.dirname):
            return BadRequest("directory " + body.dirname + " not exists")

        result = (
            new_file(body.filename, body.content)
            .and_then(lambda fl: save_file(fl))
        )

        match result:
            case Ok(file):
                print(file)
                return Success(file)
            case Err(SaveFileError() as err):
                return BadRequest(err.value)
            case _:
                return InternalServerError()
    except Exception as e:
        return InternalServerError()


@dataclass(frozen=True, slots=True)
class EditFileRequest:
    filename: str
    new_filename: str
    new_content: str


@files_router.put("/files/edit", tags=["Files"])
async def edit_file(body: EditFileRequest) -> Response:
    try:
        result = (
            fetch_file_by_name(body.filename)
            .and_then(lambda f: change_file_content(f, body.new_content) if body.new_content != "" else Ok(f))
            .and_then(lambda f: rename_file(f, body.new_filename) if body.new_filename != "" else Ok(f))
            .and_then(lambda f: update_file(body.filename, f))
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
    except Exception as e:
        return InternalServerError()
    except Exception as e:
        return InternalServerError()
