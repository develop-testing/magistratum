from __future__ import annotations

import uuid
from dataclasses import dataclass

from ...validation import validation as vld
from ..directories import directory as dirs
from ..files import files as txt

Values = dirs.Directory | dirs.RichDirectory | txt.TextFile | txt.RichTextFile


@dataclass(slots=True, frozen=True)
class NodeFilter:
    parent_id: str = ""
    type_filter: str = ""
    data_type: str = ""


@dataclass(slots=True, frozen=True)
class NodePermitions:
    owner: str
    group: str
    permitions: str


def mk_node_permitions(owner: str, group: str, permitions: str) -> NodePermitions:
    vld.validate_username(owner)
    vld.validate_name(group)
    vld.validate_permissions(permitions)
    return NodePermitions(owner, group, permitions)


@dataclass(slots=True, frozen=True)
class NodeValue:
    type: str
    content: Values


def mk_node_value(type: str, content: Values) -> NodeValue:
    if type == "directory":
        if not isinstance(content, (dirs.Directory, dirs.RichDirectory)):
            raise ValueError("invalid node value")
    elif type == "text_file":
        if not isinstance(content, (txt.TextFile, txt.RichTextFile)):
            raise ValueError("invalid node value")
    else:
        raise ValueError("invalid node value")
    return NodeValue(type, content)


@dataclass(slots=True, frozen=True)
class Node:
    id: str
    parent_id: str
    permitions: NodePermitions
    value: NodeValue


def new_node(parent_id: str, prmts: NodePermitions, value: NodeValue) -> Node:
    return mk_node(
        id=str(uuid.uuid4()),
        parent_id=parent_id,
        prmts=prmts,
        value=value,
    )


def mk_node(id: str, parent_id: str, prmts: NodePermitions, value: NodeValue) -> Node:
    vld.validate_id(id)
    if parent_id:
        vld.validate_id(parent_id)
    if not isinstance(prmts, NodePermitions):
        raise ValueError("invalid node permissions")
    if not isinstance(value, NodeValue):
        raise ValueError("invalid node value")
    return Node(id, parent_id, prmts, value)


def has_read(node: Node, user: str, groups: list[str]) -> bool:
    if user == "root":
        return True
    if node.permitions.owner == user:
        return True
    if node.permitions.group in groups:
        return "r" in node.permitions.permitions[:2]
    return "r" in node.permitions.permitions[2:]


def has_write(node: Node, user: str, groups: list[str]) -> bool:
    if user == "root":
        return True
    if node.permitions.owner == user:
        return True
    if node.permitions.group in groups:
        return "w" in node.permitions.permitions[:2]
    return "w" in node.permitions.permitions[2:]
