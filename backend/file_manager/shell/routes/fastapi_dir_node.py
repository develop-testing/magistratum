from __future__ import annotations
from fastapi import APIRouter, Request

from backend.router.response import *

from ...directories.directory import Directory
from ...directory_node import (
    BrokeNode,
    RichNode,
    mk_rich_node,
    mk_node,
    mk_node_perms,
    mk_node_meta,
)
from ...files import TextFile, TextFileFilter
from ...permissions import Permissions, has_read
from ..sources.sqlalchemy_dir import fetch_dirs_by_parent, fetch_image_by_dir
from ..sources.sqlalchemy_group import fetch_groups_by_user
from ..sources.sqlalchemy_permissions import fetch_permissions_for as fetch_perms
from ..sources.sqlalchemy_file import fetch_files_by_filter, fetch_image_by_file
from ..sources.sqlalchemy_home_dir import fetch_home_dir_by_username

dir_node_router = APIRouter()

Result = list[RichNode | BrokeNode]


def _build_nodes(
    dirs: list[Directory],
    files: list[TextFile],
    prms: list[Permissions],
    session_owner: str,
    group_names: list[str],
    images: dict[str, str],
) -> Result:
    items: list[tuple[str, str, str]] = [(d.dir_id, "dir", d.name) for d in dirs] + [
        (f.file_id, "text_file", f.name) for f in files
    ]

    result: Result = []
    for item_id, item_type, name in items:
        prm = next((p for p in prms if p.item_id == item_id), None)

        if not prm or not has_read(prm, session_owner, group_names):
            result += [
                BrokeNode(name=name, type=item_type, reason="access not allowed")
            ]
            continue

        img = images.get(item_id, "/public/img/not-found.png")

        result += [
            mk_rich_node(
                mk_node(item_type, item_id),
                mk_node_perms(
                    prm.owner_name,
                    prm.group_name,
                    prm.content[:2],
                    prm.content[2:],
                ),
                mk_node_meta(name, img),
            )
        ]

    return result


@dir_node_router.get("/directory/content", tags=["DirNode"])
async def directory_content(req: Request, dir_id: str) -> Result:
    session_owner = req.state.session.owner

    groups = fetch_groups_by_user(session_owner)
    group_names = [g.name for g in groups]

    dirs = fetch_dirs_by_parent(dir_id)
    files = fetch_files_by_filter(TextFileFilter("", "", dir_id, 0, 0))

    if not dirs and not files:
        raise BadRequest("no one dir or files not found")

    prms = fetch_perms([d.dir_id for d in dirs] + [f.file_id for f in files])
    images: dict[str, str] = {}
    for d in dirs:
        images[d.dir_id] = fetch_image_by_dir(d.dir_id)
    for f in files:
        images[f.file_id] = fetch_image_by_file(f.file_id)

    return _build_nodes(dirs, files, prms, session_owner, group_names, images)


@dir_node_router.get("/directory/home", tags=["DirNode"])
async def home_content(req: Request) -> Result:
    session_owner = req.state.session.owner

    home = fetch_home_dir_by_username(session_owner)

    groups = fetch_groups_by_user(session_owner)
    group_names = [g.name for g in groups]

    dirs = fetch_dirs_by_parent(home.dir_id)
    files = fetch_files_by_filter(TextFileFilter("", "", home.dir_id, 0, 0))

    if not dirs and not files:
        raise BadRequest("no one dir or files not found")

    prms = fetch_perms([d.dir_id for d in dirs] + [f.file_id for f in files])
    images: dict[str, str] = {}
    for d in dirs:
        images[d.dir_id] = fetch_image_by_dir(d.dir_id)
    for f in files:
        images[f.file_id] = fetch_image_by_file(f.file_id)

    return _build_nodes(dirs, files, prms, session_owner, group_names, images)
