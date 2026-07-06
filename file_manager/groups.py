from __future__ import annotations
from dataclasses import dataclass
from result import Err, Ok, Result


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


def rename_group(g: Group, new_name: str) -> Result[Group, str]:
    if new_name == "":
        return Ok(g)

    return Ok(Group(new_name, g.owner, g.members))


def change_owner(g: Group, new_owner: str) -> Result[Group, str]:
    if new_owner == "":
        return Ok(g)

    return Ok(Group(g.name, new_owner, g.members))


def add_member(g: Group, username: str) -> Result[Group, str]:
    if username in g.members:
        return Ok(g)

    return Ok(Group(g.name, g.owner, g.members + [username]))


def remove_member(g: Group, username: str) -> Result[Group, str]:
    if username not in g.members:
        return Ok(g)

    return Ok(Group(g.name, g.owner, [m for m in g.members if m != username]))


def mk_group(name: str, owner: str, members: list[str]) -> Result[Group, str]:
    members = [name] + members if name not in members else members
    return Ok(Group(name, owner, members))


def destroy_group(g: Group) -> RemovedGroup:
    return RemovedGroup(g.name)
