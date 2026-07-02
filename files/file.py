from __future__ import annotations
from dataclasses import dataclass
from result import Ok, Result


@dataclass(frozen=True, slots=True)
class File:
    name: str
    content: str


def new_file(name: str, content: str) -> Result[File, str]:
    return Ok(File(name, content))


def rename_file(f: File, new_name: str) -> Result[File, str]:
    return Ok(File(new_name, f.content))


def add_to_end_file(f: File, new_content: str) -> Result[File, str]:
    return Ok(File(f.name, f.content + new_content))


def add_to_start_file(f: File, new_content: str) -> Result[File, str]:
    return Ok(File(f.name, new_content + f.content))


def change_file_content(f: File, new_content: str) -> Result[File, str]:
    return Ok(File(f.name, new_content))


@dataclass(slots=True)
class Directory:
    name: str
    parent_name: str
    files: list[str]

def new_directory(dir_name: str, parent_name: str) -> Result[Directory, str]:
    return Ok(Directory(dir_name, parent_name, []))

def add_to_directory(d: Directory, file_name: str) -> Result[Directory, str]:
    return Ok(Directory(d.name, d.parent_name, d.files + [file_name]))


def remove_from_directory(d: Directory, file_name: str) -> Result[Directory, str]:
    if file_name not in d.files:
        return Ok(d)

    new_files = [f for f in d.files if f != file_name]

    return Ok(Directory(d.name, d.parent_name, new_files))
