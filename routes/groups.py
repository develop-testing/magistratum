from __future__ import annotations
from dataclasses import dataclass
from result import Ok, Err
from fastapi import APIRouter, Depends, Response

from .response import *

from files.groups.groups import mk_group
from files.groups.sqlalchemy_group import save_group

groups_router = APIRouter()


@dataclass(frozen=True, slots=True)
class CreateGroupRequest:
    name: str
    owner: str
    members: list[str]


@groups_router.post("/group", tags=["Groups"])
async def create_group(body: CreateGroupRequest) -> Response:
    group = mk_group(body.name, body.owner, body.members).map(
        lambda grp: save_group(grp)
    )

    match group:
        case Ok(g):
            return Success(g)
        case _:
            return InternalServerError()
