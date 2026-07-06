from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter

from ..groups import Group, mk_group
from ..sources.sqlalchemy_group import save_group

groups_router = APIRouter()


@dataclass(frozen=True, slots=True)
class CreateGroupRequest:
    name: str
    owner: str
    members: list[str]


@groups_router.post("/group", tags=["Groups"])
async def create_group(body: CreateGroupRequest) -> Group:
    g = mk_group(body.name, body.owner, body.members).unwrap()
    save_group(g)
    return g
