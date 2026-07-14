from __future__ import annotations
from dataclasses import dataclass
import re


@dataclass(frozen=True, slots=True)
class Permissions:
    item_id: str
    owner_name: str
    group_name: str
    content: str


def new_permissions(
    item_id: str, owner_name: str, group_name: str, content: str
) -> Permissions:
    if len(item_id) > 255:
        raise ValueError("wrong item id length")

    if len(owner_name) > 255:
        raise ValueError("wrong owner id length")

    if len(group_name) > 255:
        raise ValueError("wrong group id length")

    if not re.match(r"^[r-][w-][r-][w-]$", content) or not len(content) == 4:
        raise ValueError("wrong other symbols")

    return Permissions(item_id, owner_name, group_name, content)


def grant_for_group(p: Permissions, who: str, what: str) -> Permissions:
    if p.owner_name != who:
        raise PermissionError("only owner can change permissions")

    if what == "read":
        new_value = p.content[:0] + "r" + p.content[1:]
    elif what == "write":
        new_value = p.content[:1] + "w" + p.content[2:]
    else:
        raise ValueError(f"unknown action: {what}, expected read/write")

    return new_permissions(p.item_id, p.owner_name, p.group_name, new_value)


def grant_for_other(p: Permissions, who: str, what: str) -> Permissions:
    if p.owner_name != who:
        raise PermissionError("only owner can change permissions")

    if what == "read":
        new_value = p.content[:2] + "r" + p.content[3:]
    elif what == "write":
        new_value = p.content[:3] + "w" + p.content[4:]
    else:
        raise ValueError(f"unknown action: {what}, expected read/write")

    return new_permissions(p.item_id, p.owner_name, p.group_name, new_value)


def revoke_for_group(p: Permissions, who: str, what: str) -> Permissions:
    if p.owner_name != who:
        raise PermissionError("only owner can change permissions")

    if what == "read":
        new_value = p.content[:0] + "-" + p.content[1:]
    elif what == "write":
        new_value = p.content[:1] + "-" + p.content[2:]
    else:
        raise ValueError(f"unknown action: {what}, expected read/write")

    return new_permissions(p.item_id, p.owner_name, p.group_name, new_value)


def change_group(p: Permissions, new_group_name: str) -> Permissions:
    return new_permissions(p.item_id, p.owner_name, new_group_name, p.content)


def revoke_for_other(p: Permissions, who: str, what: str) -> Permissions:
    if p.owner_name != who:
        raise PermissionError("only owner can change permissions")

    if what == "read":
        new_value = p.content[:2] + "-" + p.content[3:]
    elif what == "write":
        new_value = p.content[:3] + "-" + p.content[4:]
    else:
        raise ValueError(f"unknown action: {what}, expected read/write")

    return new_permissions(p.item_id, p.owner_name, p.group_name, new_value)


def has_read(p: Permissions, user_name: str, group_names: list[str]) -> bool:
    if user_name != "" and p.owner_name == user_name:
        return True

    if p.group_name in group_names:
        return p.content[0] == "r"

    return p.content[2] == "r"


def has_write(p: Permissions, user_name: str, group_names: list[str]) -> bool:
    if user_name != "" and p.owner_name == user_name:
        return True

    if p.group_name in group_names:
        return p.content[1] == "w"

    return p.content[3] == "w"
