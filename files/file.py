from __future__ import annotations
from dataclasses import dataclass
from result import Ok, Result


@dataclass(frozen=True, slots=True)
class File:
    id: str
    name: str
    content: str


def new_file(file_id: str, name: str, content: str) -> Result[File, str]:
    return Ok(File(file_id, name, content))


def rename_file(f: File, new_name: str) -> Result[File, str]:
    return Ok(File(f.id, new_name, f.content))


def add_to_end_file(f: File, new_content: str) -> Result[File, str]:
    return Ok(File(f.id, f.name, f.content + new_content))


def add_to_start_file(f: File, new_content: str) -> Result[File, str]:
    return Ok(File(f.id, f.name, new_content + f.content))


def change_file_content(f: File, new_content: str) -> Result[File, str]:
    return Ok(File(f.id, f.name, new_content))


def new_directory(directory_id: str, parent_id: str) -> Result[Directory, str]:
    return Ok(Directory(directory_id, parent_id, []))


@dataclass(slots=True)
class Directory:
    id: str
    parent_id: str
    files: list[str]


def add_to_directory(d: Directory, file_id: str) -> Result[Directory, str]:
    return Ok(Directory(d.id, d.parent_id, d.files + [file_id]))


def remove_from_directory(d: Directory, file_id: str) -> Result[Directory, str]:
    if file_id not in d.files:
        return Ok(d)

    new_files = [f for f in d.files if f != file_id]

    return Ok(Directory(d.id, d.parent_id, new_files))
