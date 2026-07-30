from __future__ import annotations
from dataclasses import dataclass
from fastapi import APIRouter, Depends, Request

import backend.database.database as db
import backend.router.response as resp

from backend.auth.member.auth_middleware import auth_middleware
from backend.image.upload_image import save_image_file
from backend.image.image import new_image
from backend.image.sqlalchemy_image import save_image as save_image_to_db
from ..directories import directory as dirs
from ..files import files as txt
from . import node as nmd
from .node import NodeValue
from . import sqlalchemy_node as node_src
from ..groups import groups as grps, sqlalchemy_group as grps_src


node_router = APIRouter()


@dataclass(frozen=True, slots=True)
class CreateDirReq:
    name: str
    owner: str
    group: str
    permissions: str
    parent_id: str = ""


@node_router.post("/node/directory", tags=["Nodes"])
async def create_directory(req: Request, body: CreateDirReq) -> nmd.Node:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner

        if body.parent_id:
            parent = node_src.fetch_node(conn, body.parent_id)
            group_names = grps.get_group_names(
                grps_src.fetch_groups_by_user(conn, session_owner)
            )
            if not nmd.has_write(parent, session_owner, group_names):
                raise resp.Forbidden("access denied")

        dir_val = dirs.new_directory(body.name)
        node = nmd.new_node(
            body.parent_id,
            nmd.NodePermitions(body.owner, body.group, body.permissions),
            dir_val,
        )
        conn = node_src.save_node(conn, node)
        conn.commit()
        return node

    except node_src.NodeFetchError as e:
        raise resp.BadRequest(str(e))
    finally:
        conn.rollback()
        conn.close()


@dataclass(frozen=True, slots=True)
class CreateTextFileReq:
    name: str
    content: str
    parent_id: str
    owner: str
    group: str
    permissions: str


@node_router.post("/node/text_file", tags=["Nodes"])
async def create_text_file(req: Request, body: CreateTextFileReq) -> nmd.Node:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner

        if not body.parent_id:
            raise resp.BadRequest("parent_id is required")

        parent = node_src.fetch_node(conn, body.parent_id)
        group_names = grps.get_group_names(
            grps_src.fetch_groups_by_user(conn, session_owner)
        )
        if not nmd.has_write(parent, session_owner, group_names):
            raise resp.Forbidden("access denied")

        file_val = txt.new_text_file(body.name, body.content)
        node = nmd.new_node(
            body.parent_id,
            nmd.NodePermitions(body.owner, body.group, body.permissions),
            file_val,
        )
        conn = node_src.save_node(conn, node)
        conn.commit()
        return node

    except node_src.NodeFetchError as e:
        raise resp.BadRequest(str(e))
    finally:
        conn.rollback()
        conn.close()


@dataclass(frozen=True, slots=True)
class EditDirectoryReq:
    node_id: str
    new_name: str = ""
    new_parent_id: str = ""
    new_owner: str = ""
    new_group: str = ""
    new_permissions: str = ""
    new_cover: str = ""


@node_router.patch("/node/directory/{node_id}", tags=["Nodes"])
async def edit_directory(
    req: Request, body: EditDirectoryReq
) -> nmd.Node:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner
        group_names = grps.get_group_names(
            grps_src.fetch_groups_by_user(conn, session_owner)
        )

        node = node_src.fetch_node(conn, body.node_id)
        if not nmd.has_write(node, session_owner, group_names):
            raise resp.Forbidden("access denied")

        new_content = node.value.content
        if body.new_name:
            if not isinstance(node.value.content, dirs.Directory):
                raise resp.BadRequest("node is not a directory")
            new_content = dirs.rename_directory(node.value.content, body.new_name)

        new_parent = body.new_parent_id or node.parent_id
        if new_parent == "root":
            new_parent = ""
        new_owner = body.new_owner or node.permitions.owner
        new_group = body.new_group or node.permitions.group
        new_perms = body.new_permissions or node.permitions.permitions

        node = nmd.Node(
            node.id, new_parent,
            nmd.NodePermitions(new_owner, new_group, new_perms),
            NodeValue("directory", new_content),
        )

        conn = node_src.update_node(conn, node)

        if body.new_cover:
            src = save_image_file(body.new_cover)
            image = new_image(src)
            conn = save_image_to_db(conn, image)
            conn = node_src.add_image_to_dir(conn, node.id, image.id)

        conn.commit()
        return node

    except node_src.NodeFetchError as e:
        raise resp.BadRequest(str(e))
    finally:
        conn.rollback()
        conn.close()


@dataclass(frozen=True, slots=True)
class EditTextFileReq:
    node_id: str
    new_name: str = ""
    new_content: str = ""
    new_parent_id: str = ""
    new_owner: str = ""
    new_group: str = ""
    new_permissions: str = ""
    new_cover: str = ""


@node_router.patch("/node/text_file/{node_id}", tags=["Nodes"])
async def edit_text_file(
    req: Request, body: EditTextFileReq
) -> nmd.Node:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner
        group_names = grps.get_group_names(
            grps_src.fetch_groups_by_user(conn, session_owner)
        )

        node = node_src.fetch_node(conn, body.node_id)
        if not nmd.has_write(node, session_owner, group_names):
            raise resp.Forbidden("access denied")

        new_content = node.value.content
        if body.new_name:
            if not isinstance(node.value.content, txt.TextFile):
                raise resp.BadRequest("node is not a text file")
            new_content = txt.rename_text_file(node.value.content, body.new_name)
        if body.new_content:
            if not isinstance(new_content, txt.TextFile):
                raise resp.BadRequest("node is not a text file")
            new_content = txt.change_text_file_content(new_content, body.new_content)

        new_parent = body.new_parent_id or node.parent_id
        if new_parent == "root":
            new_parent = ""
        new_owner = body.new_owner or node.permitions.owner
        new_group = body.new_group or node.permitions.group
        new_perms = body.new_permissions or node.permitions.permitions

        node = nmd.Node(
            node.id, new_parent,
            nmd.NodePermitions(new_owner, new_group, new_perms),
            NodeValue("text_file", new_content),
        )

        conn = node_src.update_node(conn, node)

        if body.new_cover:
            src = save_image_file(body.new_cover)
            image = new_image(src)
            conn = save_image_to_db(conn, image)
            conn = node_src.add_image_to_file(conn, node.id, image.id)

        conn.commit()
        return node

    except node_src.NodeFetchError as e:
        raise resp.BadRequest(str(e))
    finally:
        conn.rollback()
        conn.close()


@node_router.get("/nodes", tags=["Nodes"])
async def read_nodes(req: Request, fltr: nmd.NodeFilter = Depends()) -> list[nmd.Node]:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner
        group_names = grps.get_group_names(
            grps_src.fetch_groups_by_user(conn, session_owner)
        )

        nodes = node_src.fetch_nodes(conn, fltr)

        result: list[nmd.Node] = []
        for n in nodes:
            if nmd.has_read(n, session_owner, group_names):
                if fltr.data_type == "rich":
                    if isinstance(n.value.content, txt.TextFile):
                        src = node_src.fetch_image_by_file(conn, n.id) or "/public/img/not-found.png"
                        n = nmd.Node(
                            n.id, n.parent_id, n.permitions,
                            NodeValue("text_file", txt.RichTextFile(n.value.content, txt.Decoration(src))),
                        )
                    elif isinstance(n.value.content, dirs.Directory):
                        src = node_src.fetch_image_by_dir(conn, n.id) or "/public/img/not-found.png"
                        n = nmd.Node(
                            n.id, n.parent_id, n.permitions,
                            NodeValue("directory", dirs.RichDirectory(n.value.content, txt.Decoration(src))),
                        )
                result.append(n)
        return result

    finally:
        conn.rollback()
        conn.close()


@node_router.get("/node/{node_id}", tags=["Nodes"])
async def read_node(req: Request, node_id: str, data_type: str = "") -> nmd.Node:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner
        group_names = grps.get_group_names(
            grps_src.fetch_groups_by_user(conn, session_owner)
        )

        node = node_src.fetch_node(conn, node_id)
        if not nmd.has_read(node, session_owner, group_names):
            raise resp.Forbidden("access denied")

        if data_type == "rich":
            if isinstance(node.value.content, txt.TextFile):
                src = node_src.fetch_image_by_file(conn, node_id) or "/public/img/not-found.png"
                node = nmd.Node(
                    node.id, node.parent_id, node.permitions,
                    NodeValue("text_file", txt.RichTextFile(node.value.content, txt.Decoration(src))),
                )
            elif isinstance(node.value.content, dirs.Directory):
                src = node_src.fetch_image_by_dir(conn, node_id) or "/public/img/not-found.png"
                node = nmd.Node(
                    node.id, node.parent_id, node.permitions,
                    NodeValue("directory", dirs.RichDirectory(node.value.content, txt.Decoration(src))),
                )

        return node

    except node_src.NodeFetchError as e:
        raise resp.BadRequest(str(e))
    finally:
        conn.rollback()
        conn.close()


@node_router.delete("/node/{node_id}", tags=["Nodes"])
async def delete_node(req: Request, node_id: str) -> bool:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner
        group_names = grps.get_group_names(
            grps_src.fetch_groups_by_user(conn, session_owner)
        )

        node = node_src.fetch_node(conn, node_id)
        if not nmd.has_write(node, session_owner, group_names):
            raise resp.Forbidden("access denied")

        conn = node_src.delete_node(conn, node_id)
        conn.commit()
        return True

    except node_src.NodeFetchError as e:
        raise resp.BadRequest(str(e))
    finally:
        conn.rollback()
        conn.close()
