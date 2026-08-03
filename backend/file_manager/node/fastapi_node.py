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

            groups = grps_src.fetch_groups_by_user(conn, session_owner)
            group_names = grps.get_group_names(groups)

            if not nmd.has_write(parent, session_owner, group_names):
                raise resp.Forbidden("access denied")

        dir_val = dirs.mk_directory(body.name)
        node_perms = nmd.mk_node_permitions(body.owner, body.group, body.permissions)
        node_value = nmd.mk_node_value("directory", dir_val)
        node = nmd.new_node(body.parent_id, node_perms, node_value)

        conn = node_src.save_node(conn, node)
        conn.commit()

        return node

    except node_src.NodeFetchError as e:
        raise resp.BadRequest(str(e))
    finally:
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
        groups = grps_src.fetch_groups_by_user(conn, session_owner)
        group_names = grps.get_group_names(groups)

        if not nmd.has_write(parent, session_owner, group_names):
            raise resp.Forbidden("access denied")

        file_val = txt.mk_text_file(body.name, body.content)
        node_perms = nmd.mk_node_permitions(body.owner, body.group, body.permissions)
        node_value = nmd.mk_node_value("text_file", file_val)
        node = nmd.new_node(body.parent_id, node_perms, node_value)

        conn = node_src.save_node(conn, node)
        conn.commit()

        return node

    except node_src.NodeFetchError as e:
        raise resp.BadRequest(str(e))
    finally:
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
async def edit_directory(req: Request, body: EditDirectoryReq) -> nmd.Node:
    cnn = db.engine.connect()
    try:
        session_owner = req.state.session.owner

        groups = grps_src.fetch_groups_by_user(cnn, session_owner)
        group_names = grps.get_group_names(groups)
        node = node_src.fetch_node(cnn, body.node_id)

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

        node_perms = nmd.mk_node_permitions(new_owner, new_group, new_perms)
        node_value = nmd.mk_node_value("directory", new_content)
        node = nmd.mk_node(node.id, new_parent, node_perms, node_value)

        cnn = node_src.update_node(cnn, node)

        if body.new_owner or body.new_group or body.new_permissions:
            cnn = node_src.update_perms(cnn, node.id, new_owner, new_group, new_perms)

        if body.new_cover:
            src = save_image_file(body.new_cover)
            image = new_image(src)
            cnn = save_image_to_db(cnn, image)
            cnn = node_src.add_image_to_dir(cnn, node.id, image.id)

        cnn.commit()

        return node

    except node_src.NodeFetchError as e:
        raise resp.BadRequest(str(e))
    finally:
        cnn.close()


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
async def edit_text_file(req: Request, body: EditTextFileReq) -> nmd.Node:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner

        groups = grps_src.fetch_groups_by_user(conn, session_owner)
        group_names = grps.get_group_names(groups)
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

        node_perms = nmd.mk_node_permitions(new_owner, new_group, new_perms)
        node_value = nmd.mk_node_value("text_file", new_content)
        node = nmd.mk_node(node.id, new_parent, node_perms, node_value)

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
        conn.close()


Filter = nmd.NodeFilter
ReadResult = list[nmd.Node]


@node_router.get("/nodes", tags=["Nodes"])
async def read_nodes(req: Request, fltr: Filter = Depends()) -> ReadResult:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner

        groups = grps_src.fetch_groups_by_user(conn, session_owner)
        group_names = grps.get_group_names(groups)

        nodes = node_src.fetch_nodes(conn, fltr)

        visible: list[nmd.Node] = []
        for n in nodes:
            if nmd.has_read(n, session_owner, group_names):
                visible.append(n)

        if fltr.data_type != "rich":
            return visible

        def_img = "/public/img/not-found.png"
        covers = node_src.fetch_cover_images(conn, [n.id for n in visible])

        result: list[nmd.Node] = []

        for n in visible:
            img_src = covers.get(n.id, def_img)

            if isinstance(n.value.content, txt.TextFile):
                rich_file = txt.mk_rich_text_file(
                    n.value.content, txt.mk_decoration(img_src)
                )
                node_value = nmd.mk_node_value("text_file", rich_file)

            elif isinstance(n.value.content, dirs.Directory):
                rich_dir = dirs.mk_rich_directory(
                    n.value.content, txt.mk_decoration(img_src)
                )
                node_value = nmd.mk_node_value("directory", rich_dir)
            else:
                raise resp.BadRequest("unexpected node content")

            result.append(nmd.mk_node(n.id, n.parent_id, n.permitions, node_value))

        return result

    finally:
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

        if data_type != "rich":
            return node

        def_img = "/public/img/not-found.png"

        if isinstance(node.value.content, txt.TextFile):
            img_src = node_src.fetch_image_by_file(conn, node_id) or def_img
            rich_file = txt.mk_rich_text_file(
                node.value.content, txt.mk_decoration(img_src)
            )
            node_value = nmd.mk_node_value("text_file", rich_file)
        elif isinstance(node.value.content, dirs.Directory):
            img_src = node_src.fetch_image_by_dir(conn, node_id) or def_img
            rich_dir = dirs.mk_rich_directory(
                node.value.content, txt.mk_decoration(img_src)
            )
            node_value = nmd.mk_node_value("directory", rich_dir)
        else:
            raise resp.BadRequest("unexpected node content")

        return nmd.mk_node(node.id, node.parent_id, node.permitions, node_value)
    except node_src.NodeFetchError as e:
        raise resp.BadRequest(str(e))
    finally:
        conn.close()


@node_router.delete("/node/{node_id}", tags=["Nodes"])
async def delete_node(req: Request, node_id: str) -> bool:
    conn = db.engine.connect()
    try:
        session_owner = req.state.session.owner

        groups = grps_src.fetch_groups_by_user(conn, session_owner)
        group_names = grps.get_group_names(groups)
        node = node_src.fetch_node(conn, node_id)

        if not nmd.has_write(node, session_owner, group_names):
            raise resp.Forbidden("access denied")

        conn = node_src.delete_node(conn, node_id)
        conn.commit()
        return True

    except node_src.NodeFetchError as e:
        raise resp.BadRequest(str(e))
    finally:
        conn.close()
