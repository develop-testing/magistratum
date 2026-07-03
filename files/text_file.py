from __future__ import annotations
from dataclasses import dataclass
from result import Ok, Result


@dataclass(frozen=True, slots=True)
class TextFileFilter:
    by_name: str
    by_directory: str
    limit: int
    offset: int


@dataclass(frozen=True, slots=True)
class TextFile:
    name: str
    content: str


def new_file(name: str, content: str) -> Result[TextFile, str]:
    return Ok(TextFile(name, content))


def rename_file(f: TextFile, new_name: str) -> Result[TextFile, str]:
    if new_name == "":
        return Ok(f)

    return Ok(TextFile(new_name, f.content))


def add_to_end_file(f: TextFile, new_content: str) -> Result[TextFile, str]:
    return Ok(TextFile(f.name, f.content + new_content))


def add_to_start_file(f: TextFile, new_content: str) -> Result[TextFile, str]:
    return Ok(TextFile(f.name, new_content + f.content))


def change_file_content(f: TextFile, new_content: str) -> Result[TextFile, str]:
    if new_content == "":
        return Ok(f)

    return Ok(TextFile(f.name, new_content))
