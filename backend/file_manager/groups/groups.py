from __future__ import annotations
from dataclasses import dataclass

from ...validation import validation as vld


@dataclass(frozen=True, slots=True)
class Group:
    name: str
    owner: str
    members: list[str]


@dataclass(frozen=True, slots=True)
class RemovedGroup:
    name: str


@dataclass(frozen=True, slots=True)
class FetchGroupReq:
    owner: str = ""
    member: str = ""


def rename_group(g: Group, new_name: str) -> Group:
    if new_name == "":
        return g

    return mk_group(new_name, g.owner, g.members)


def change_owner(g: Group, new_owner: str) -> Group:
    if new_owner == "":
        return g

    return mk_group(g.name, new_owner, g.members)


def add_member(g: Group, username: str) -> Group:
    if username in g.members:
        return g

    return mk_group(g.name, g.owner, g.members + [username])


def remove_member(g: Group, username: str) -> Group:
    if username not in g.members:
        return g

    return mk_group(g.name, g.owner, [m for m in g.members if m != username])


def mk_group(name: str, owner: str, members: list[str]) -> Group:
    vld.validate_name(name)
    vld.validate_username(owner)
    members = [name] + members if name not in members else members
    for m in members:
        vld.validate_name(m)
    return Group(name, owner, members)


def mk_removed_group(name: str) -> RemovedGroup:
    vld.validate_name(name)
    return RemovedGroup(name)


def destroy_group(g: Group) -> RemovedGroup:
    return mk_removed_group(g.name)


def get_group_names(groups: list[Group]) -> list[str]:
    return [g.name for g in groups]
