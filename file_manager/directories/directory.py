from __future__ import annotations
from dataclasses import dataclass

import uuid


@dataclass(frozen=True, slots=True)
class DirFilter:
    only_can_read: bool = False
    only_can_write: bool = False
    parent_id: str = ""
    by_id: str = ""
    by_name: str = ""


@dataclass(frozen=True, slots=True)
class BrokenDirectory:
    name: str
    reason: str


@dataclass(slots=True)
class Directory:
    dir_id: str
    name: str
    parent_id: str
    files: list[str]


def destroy_directory(d: Directory) -> str:
    return d.dir_id


def mk_directory(dir_name: str, parent_id: str) -> Directory:
    return Directory("dir@" + str(uuid.uuid4()), dir_name, parent_id, [])


def mk_broken_directory(name: str, reason: str) -> BrokenDirectory:
    return BrokenDirectory(name, reason)


def rename_directory(d: Directory, new_name: str) -> Directory:
    if new_name == "":
        return d

    return Directory(d.dir_id, new_name, d.parent_id, d.files)


def change_directory_parent(d: Directory, new_parent_id: str) -> Directory:
    if new_parent_id == "":
        return d

    return Directory(d.dir_id, d.name, new_parent_id, d.files)


def add_to_directory(d: Directory, file_name: str) -> Directory:
    return Directory(d.dir_id, d.name, d.parent_id, d.files + [file_name])


def remove_from_directory(d: Directory, file_name: str) -> Directory:
    if file_name not in d.files:
        return d

    new_files = [f for f in d.files if f != file_name]

    return Directory(d.dir_id, d.name, d.parent_id, new_files)
