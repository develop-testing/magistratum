from __future__ import annotations
from dataclasses import dataclass
from result import Ok, Result

import uuid


@dataclass(frozen=True, slots=True)
class DirFilter:
    parent_id: str = ""


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


def mk_directory(dir_name: str, parent_id: str) -> Result[Directory, str]:
    return Ok(Directory("dir@" + str(uuid.uuid4()), dir_name, parent_id, []))


def rename_directory(d: Directory, new_name: str) -> Result[Directory, str]:
    if new_name == "":
        return Ok(d)

    return Ok(Directory(d.dir_id, new_name, d.parent_id, d.files))


def change_directory_parent(d: Directory, new_parent_id: str) -> Result[Directory, str]:
    if new_parent_id == "":
        return Ok(d)

    return Ok(Directory(d.dir_id, d.name, new_parent_id, d.files))


def add_to_directory(d: Directory, file_name: str) -> Result[Directory, str]:
    return Ok(Directory(d.dir_id, d.name, d.parent_id, d.files + [file_name]))


def remove_from_directory(d: Directory, file_name: str) -> Result[Directory, str]:
    if file_name not in d.files:
        return Ok(d)

    new_files = [f for f in d.files if f != file_name]

    return Ok(Directory(d.dir_id, d.name, d.parent_id, new_files))
