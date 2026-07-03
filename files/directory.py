from __future__ import annotations
from dataclasses import dataclass
from result import Ok, Result

import uuid


@dataclass(slots=True)
class Directory:
    dir_id: str
    name: str
    parent_id: str
    files: list[str]


def mk_directory(dir_name: str, parent_id: str) -> Result[Directory, str]:
    return Ok(Directory("dir#" + str(uuid.uuid4()), dir_name, parent_id, []))


def add_to_directory(d: Directory, file_name: str) -> Result[Directory, str]:
    return Ok(Directory(d.dir_id, d.name, d.parent_id, d.files + [file_name]))


def remove_from_directory(d: Directory, file_name: str) -> Result[Directory, str]:
    if file_name not in d.files:
        return Ok(d)

    new_files = [f for f in d.files if f != file_name]

    return Ok(Directory(d.dir_id, d.name, d.parent_id, new_files))
