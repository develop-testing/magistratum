from __future__ import annotations
from fastapi import APIRouter, Request

from router.response import *

from ..directory_node import (
    BrokeNode,
    DirNode,
    Perms,
    RichDirNode,
    mk_dir_item,
    mk_item_perms,
    mk_rich_dir_item,
)
from ..files import TextFileFilter
from ..permissions import has_read
from ..sources.sqlalchemy_dir import fetch_dirs_by_parent
from ..sources.sqlalchemy_group import fetch_groups_by_user
from ..sources.sqlalchemy_permissions import fetch_permissions_for
from ..sources.sqlalchemy_file import fetch_file_by_filter

dir_node_router = APIRouter()

Result = list[RichDirNode | BrokeNode]


@dir_node_router.get("/directory/content", tags=["Directories"])
async def directory_content(req: Request, dir_id: str) -> Result:
    session_owner = req.state.session.owner

    groups = fetch_groups_by_user(session_owner)
    group_names = [g.name for g in groups]

    dirs = fetch_dirs_by_parent(dir_id)

    files = fetch_file_by_filter(TextFileFilter("", dir_id, 0, 0))

    if not dirs and not files:
        raise BadRequest("no one dir or files not found")

    prms = fetch_permissions_for([d.dir_id for d in dirs] + [f.file_id for f in files])

    result: Result = []

    for d in dirs:
        prm = next((p for p in prms if p.item_id == d.dir_id), None)

        if not prm or not has_read(prm, session_owner, group_names):
            result += [BrokeNode(name=d.name, type="dir", reason="access not allowed")]
            continue

        result += [
            mk_rich_dir_item(
                mk_dir_item("dir", d.dir_id),
                mk_item_perms(prm.content[:2], prm.content[2:]),
                prm.owner_name,
                prm.group_name,
            )
        ]

    for f in files:
        prm = next((p for p in prms if p.item_id == f.file_id), None)

        if not prm or not has_read(prm, session_owner, group_names):
            result += [
                BrokeNode(name=f.name, type="text_file", reason="access not allowed")
            ]
            continue

        result += [
            mk_rich_dir_item(
                mk_dir_item("text_file", f.file_id),
                mk_item_perms(prm.content[:2], prm.content[2:]),
                prm.owner_name,
                prm.group_name,
            )
        ]

    return result
