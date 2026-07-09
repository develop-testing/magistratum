from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BrokeNode:
    name: str
    type: str
    reason: str


@dataclass(frozen=True, slots=True)
class DirNode:
    type: str
    node_id: str


@dataclass(frozen=True, slots=True)
class Perms:
    group: str
    other: str


@dataclass(frozen=True, slots=True)
class RichDirNode:
    node: DirNode
    perms: Perms
    owner_name: str
    group_name: str


def mk_dir_item(type: str, node_id: str) -> DirNode:
    return DirNode(type, node_id)


def mk_item_perms(group: str, other: str) -> Perms:
    return Perms(group, other)


def mk_rich_dir_item(
    node: DirNode, perms: Perms, owner_name: str, group_name: str
) -> RichDirNode:
    return RichDirNode(node, perms, owner_name, group_name)
