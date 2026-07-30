from __future__ import annotations
from dataclasses import dataclass

import uuid

from ..directories import directory as dirs
from ..files import files as txt


Values = dirs.Directory | txt.TextFile


@dataclass(slots=True, frozen=True)
class NodePermitions:
    owner: str
    group: str
    permitions: str


@dataclass(slots=True, frozen=True)
class NodeValue:
    type: str
    content: Values


@dataclass(slots=True, frozen=True)
class Node:
    id: str
    parent_id: str
    permitions: NodePermitions
    value: NodeValue


@dataclass(slots=True, frozen=True)
class NodeFilter:
    parent_id: str = ""
    type_filter: str = ""


def new_node(parent_id: str, permitions: NodePermitions, content: Values) -> Node:
    typ = "directory" if isinstance(content, dirs.Directory) else "text_file"
    return Node(
        id=str(uuid.uuid4()),
        parent_id=parent_id,
        permitions=permitions,
        value=NodeValue(typ, content),
    )

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

