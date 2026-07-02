from __future__ import annotations
from dataclasses import dataclass
import re
from result import Err, Ok, Result


@dataclass(slots=True)
class PermissionsFilter:
    item_id: str


@dataclass(frozen=True, slots=True)
class Permissions:
    item_id: str
    owner_id: str
    group_id: str
    values: str


def new_permissions(
    item_id: str, owner_id: str, group_id: str, values: str
) -> Result[Permissions, str]:
    if len(item_id) > 255:
        return Err("item_id too long")

    if len(owner_id) > 255:
        return Err("wrong owner id length")

    if len(group_id) > 255:
        return Err("wrong group id length")

    if not re.match(r"^[r-][w-][r-][w-]$", values) or not len(values) == 4:
        return Err("wrong other symbols")

    return Ok(Permissions(item_id, owner_id, group_id, values))


def grant_for_group(p: Permissions, who: str, what: str) -> Result[Permissions, str]:
    if p.owner_id != who:
        return Err("only owner can change permissions")

    if what == "read":
        new_value = p.values[:0] + "r" + p.values[1:]
    elif what == "write":
        new_value = p.values[:1] + "w" + p.values[2:]
    else:
        return Err(f"unknown action: {what}, expected read/write")

    return new_permissions(p.item_id, p.owner_id, p.group_id, new_value)


def grant_for_other(p: Permissions, who: str, what: str) -> Result[Permissions, str]:
    if p.owner_id != who:
        return Err("only owner can change permissions")

    if what == "read":
        new_value = p.values[:2] + "r" + p.values[3:]
    elif what == "write":
        new_value = p.values[:3] + "w" + p.values[4:]
    else:
        return Err(f"unknown action: {what}, expected read/write")

    return new_permissions(p.item_id, p.owner_id, p.group_id, new_value)


def revoke_for_group(p: Permissions, who: str, what: str) -> Result[Permissions, str]:
    if p.owner_id != who:
        return Err("only owner can change permissions")

    if what == "read":
        new_value = p.values[:0] + "-" + p.values[1:]
    elif what == "write":
        new_value = p.values[:1] + "-" + p.values[2:]
    else:
        return Err(f"unknown action: {what}, expected read/write")

    return new_permissions(p.item_id, p.owner_id, p.group_id, new_value)


def revoke_for_other(p: Permissions, who: str, what: str) -> Result[Permissions, str]:
    if p.owner_id != who:
        return Err("only owner can change permissions")

    if what == "read":
        new_value = p.values[:2] + "-" + p.values[3:]
    elif what == "write":
        new_value = p.values[:3] + "-" + p.values[4:]
    else:
        return Err(f"unknown action: {what}, expected read/write")

    return new_permissions(p.item_id, p.owner_id, p.group_id, new_value)


def has_permissions(p: Permissions, action: str, user_id: str, group_id: str) -> bool:
    if user_id != "" and p.owner_id == user_id:
        return True

    if group_id != "" and p.group_id == group_id:
        if action == "read":
            return p.values[0] == "r"
        if action == "write":
            return p.values[1] == "w"

    if action == "read":
        return p.values[2] == "r"
    elif action == "write":
        return p.values[3] == "w"

    return False
