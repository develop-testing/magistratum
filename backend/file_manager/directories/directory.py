from __future__ import annotations
from dataclasses import dataclass

import uuid

from backend.file_manager.permissions.permissions import Permissions


@dataclass(frozen=True, slots=True)
class DirFilter:
    only_can_write: bool = False
    parent_id: str = ""
    by_id: str = ""
    by_name: str = ""
    data_type: str = "min"


@dataclass(frozen=True, slots=True)
class BrokenDirectory:
    name: str
    reason: str


@dataclass(slots=True)
class Directory:
    dir_id: str
    name: str
    parent_id: str | None


@dataclass(frozen=True, slots=True)
class RichDirectory:
    directory: Directory
    perms: Permissions
    image: str


def mk_rich_directory(d: Directory, perms: Permissions, image: str) -> RichDirectory:
    return RichDirectory(d, perms, image)


def new_directory(dir_name: str, parent_id: str) -> Directory:
    return Directory("dir@" + str(uuid.uuid4()), dir_name, parent_id)


def mk_directory(dir_id: str, name: str, parent_id: str | None) -> Directory:
    return Directory(dir_id, name, parent_id)


def mk_broken_directory(name: str, reason: str) -> BrokenDirectory:
    return BrokenDirectory(name, reason)


def rename_directory(d: Directory, new_name: str) -> Directory:
    if new_name == "":
        return d

    return Directory(d.dir_id, new_name, d.parent_id)


def change_directory_parent(d: Directory, new_parent_id: str) -> Directory:
    if not new_parent_id:
        return d

    return Directory(d.dir_id, d.name, new_parent_id)
