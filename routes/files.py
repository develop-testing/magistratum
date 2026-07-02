from __future__ import annotations
from dataclasses import dataclass
from result import Ok, Err, Result
from fastapi import APIRouter, Request, Response

from .response import *
from files.file import *
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
