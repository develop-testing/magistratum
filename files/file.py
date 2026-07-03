from __future__ import annotations
from dataclasses import dataclass
from result import Ok, Result


@dataclass(frozen=True, slots=True)
class FileFilter:
    by_name: str
    by_directory: str
    limit: int
    offset: int


@dataclass(frozen=True, slots=True)
class File:
    name: str
    content: str


def new_file(name: str, content: str) -> Result[File, str]:
    return Ok(File(name, content))


def rename_file(f: File, new_name: str) -> Result[File, str]:
    if new_name == "":
        return Ok(f)

    return Ok(File(new_name, f.content))


def add_to_end_file(f: File, new_content: str) -> Result[File, str]:
    return Ok(File(f.name, f.content + new_content))


def add_to_start_file(f: File, new_content: str) -> Result[File, str]:
    return Ok(File(f.name, new_content + f.content))


def change_file_content(f: File, new_content: str) -> Result[File, str]:
    if new_content == "":
        return Ok(f)

    return Ok(File(f.name, new_content))
