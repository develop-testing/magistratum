from __future__ import annotations
from dataclasses import dataclass
import re
from result import Err, Ok, Result


@dataclass(frozen=True, slots=True)
class PermissionDenied:
    value: str


@dataclass(frozen=True, slots=True)
class PermissionValidationError:
    value: str


@dataclass(frozen=True, slots=True)
class Permissions:
    item_id: str
    owner_name: str
    group_name: str
    content: str


PermErrs = PermissionDenied | PermissionValidationError


def new_permissions(
    item_id: str, owner_name: str, group_name: str, content: str
) -> Result[Permissions, PermErrs]:
    if len(item_id) > 255:
        return Err(PermissionValidationError("wrong item id length"))

    if len(owner_name) > 255:
        return Err(PermissionValidationError("wrong owner id length"))

    if len(group_name) > 255:
        return Err(PermissionValidationError("wrong group id length"))

    if not re.match(r"^[r-][w-][r-][w-]$", content) or not len(content) == 4:
        return Err(PermissionValidationError("wrong other symbols"))

    return Ok(Permissions(item_id, owner_name, group_name, content))


def grant_for_group(
    p: Permissions, who: str, what: str
) -> Result[Permissions, PermErrs]:
    if p.owner_name != who:
        return Err(PermissionDenied("only owner can change permissions"))

    if what == "read":
        new_value = p.content[:0] + "r" + p.content[1:]
    elif what == "write":
        new_value = p.content[:1] + "w" + p.content[2:]
    else:
        return Err(
            PermissionValidationError(f"unknown action: {what}, expected read/write")
        )

    return new_permissions(p.item_id, p.owner_name, p.group_name, new_value)


def grant_for_other(
    p: Permissions, who: str, what: str
) -> Result[Permissions, PermErrs]:
    if p.owner_name != who:
        return Err(PermissionDenied("only owner can change permissions"))

    if what == "read":
        new_value = p.content[:2] + "r" + p.content[3:]
    elif what == "write":
        new_value = p.content[:3] + "w" + p.content[4:]
    else:
        return Err(
            PermissionValidationError(f"unknown action: {what}, expected read/write")
        )

    return new_permissions(p.item_id, p.owner_name, p.group_name, new_value)


def revoke_for_group(
    p: Permissions, who: str, what: str
) -> Result[Permissions, PermErrs]:
    if p.owner_name != who:
        return Err(PermissionDenied("only owner can change permissions"))

    if what == "read":
        new_value = p.content[:0] + "-" + p.content[1:]
    elif what == "write":
        new_value = p.content[:1] + "-" + p.content[2:]
    else:
        return Err(
            PermissionValidationError(f"unknown action: {what}, expected read/write")
        )

    return new_permissions(p.item_id, p.owner_name, p.group_name, new_value)


def revoke_for_other(
    p: Permissions, who: str, what: str
) -> Result[Permissions, PermErrs]:
    if p.owner_name != who:
        return Err(PermissionDenied("only owner can change permissions"))

    if what == "read":
        new_value = p.content[:2] + "-" + p.content[3:]
    elif what == "write":
        new_value = p.content[:3] + "-" + p.content[4:]
    else:
        return Err(
            PermissionValidationError(f"unknown action: {what}, expected read/write")
        )

    return new_permissions(p.item_id, p.owner_name, p.group_name, new_value)


def has_permissions(p: Permissions, action: str, user_name: str, group_name: str) -> bool:
    if user_name != "" and p.owner_name == user_name:
        return True

    if group_name != "" and p.group_name == group_name:
        if action == "read":
            return p.content[0] == "r"
        if action == "write":
            return p.content[1] == "w"

    if action == "read":
        return p.content[2] == "r"
    elif action == "write":
        return p.content[3] == "w"

    return False
