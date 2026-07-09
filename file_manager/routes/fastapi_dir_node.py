from __future__ import annotations
from fastapi import APIRouter, Request

from router.response import *

from ..directory_node import (
    BrokeNode,
    RichNode,
    mk_rich_node,
    mk_node,
    mk_node_perms,
    mk_node_meta,
)
from ..files import TextFileFilter
from ..permissions import has_read
from ..sources.sqlalchemy_dir import fetch_dirs_by_parent
from ..sources.sqlalchemy_group import fetch_groups_by_user
from ..sources.sqlalchemy_permissions import fetch_permissions_for
from ..sources.sqlalchemy_file import fetch_file_by_filter

dir_node_router = APIRouter()

Result = list[RichNode | BrokeNode]


@dir_node_router.get("/directory/content", tags=["DirNode"])
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
            mk_rich_node(
                mk_node("dir", d.dir_id),
                mk_node_perms(
                    prm.owner_name,
                    prm.group_name,
                    prm.content[:2],
                    prm.content[2:],
                ),
                mk_node_meta(
                    d.name,
                    "https://byzantium-blogger.blog/wp-content/uploads/2020/03/2600-skull.jpg?w=1024&h=576",
                ),
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
            mk_rich_node(
                mk_node("text_file", f.file_id),
                mk_node_perms(
                    prm.owner_name, prm.group_name, prm.content[:2], prm.content[2:]
                ),
                mk_node_meta(
                    d.name,
                    "https://byzantium-blogger.blog/wp-content/uploads/2020/03/2600-skull.jpg?w=1024&h=576",
                ),
            )
        ]

    return result
