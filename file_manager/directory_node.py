from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BrokeNode:
    name: str
    type: str
    reason: str


@dataclass(frozen=True, slots=True)
class Node:
    type: str
    node_id: str


@dataclass(frozen=True, slots=True)
class Perms:
    owner_name: str
    group_name: str
    group: str
    other: str


@dataclass(frozen=True, slots=True)
class NodeMeta:
    name: str
    img: str


@dataclass(frozen=True, slots=True)
class RichNode:
    node: Node
    perms: Perms
    meta: NodeMeta


def mk_node(type: str, node_id: str) -> Node:
    return Node(type, node_id)


def mk_node_perms(owner_name: str, group_name: str, group: str, other: str) -> Perms:
    return Perms(owner_name, group_name, group, other)


def mk_node_meta(name: str, img: str) -> NodeMeta:
    return NodeMeta(name, img)


def mk_rich_node(node: Node, perms: Perms, meta: NodeMeta) -> RichNode:
    return RichNode(node, perms, meta)
