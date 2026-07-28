from __future__ import annotations
from dataclasses import dataclass

import uuid

from backend.file_manager.permissions.permissions import Permissions


@dataclass(frozen=True, slots=True)
class TextFileFilter:
    by_id: str = ""
    by_name: str = ""
    by_directory: str = ""
    limit: int = 10
    offset: int = 0
    data_type: str = "min"


@dataclass(frozen=True, slots=True)
class RemovedFile:
    file_id: str


@dataclass(frozen=True, slots=True)
class BrokenFile:
    name: str
    reason: str


@dataclass(frozen=True, slots=True)
class TextFile:
    file_id: str
    name: str
    content: str
    parent_id: str


@dataclass(frozen=True, slots=True)
class RichTextFile:
    text_file: TextFile
    perms: Permissions
    image: str


def mk_rich_text_file(file: TextFile, perms: Permissions, image: str) -> RichTextFile:
    return RichTextFile(file, perms, image)


def mk_broken_file(name: str, reason: str) -> BrokenFile:
    return BrokenFile(name, reason)


def mk_text_file(id: str, name: str, content: str, parent_id: str = "") -> TextFile:
    return TextFile(id, name, content, parent_id)


def new_file(name: str, content: str, parent_id: str = "") -> TextFile:
    return mk_text_file("text-file@" + str(uuid.uuid4()), name, content, parent_id)


def name_of_file(f: TextFile | RichTextFile | BrokenFile) -> str:
    match (f):
        case TextFile():
            return f.name
        case RichTextFile():
            return f.text_file.name
        case BrokenFile():
            return f.name


def id_of_file(f: TextFile | RichTextFile | BrokenFile) -> str:
    match (f):
        case TextFile():
            return f.file_id
        case RichTextFile():
            return f.text_file.file_id
        case BrokenFile():
            return ""


def copy_file_to(fl: TextFile, parent_id: str) -> TextFile:
    return new_file(fl.name, fl.content, parent_id)


def rename_file(f: TextFile, new_name: str) -> TextFile:
    if new_name == "":
        return f

    return TextFile(f.file_id, new_name, f.content, f.parent_id)


def add_to_end_file(f: TextFile, new_content: str) -> TextFile:
    return TextFile(f.file_id, f.name, f.content + new_content, f.parent_id)


def add_to_start_file(f: TextFile, new_content: str) -> TextFile:
    return TextFile(f.file_id, f.name, new_content + f.content, f.parent_id)


def change_file_parent(f: TextFile, new_parent_id: str) -> TextFile:
    if new_parent_id == "":
        return f

    return TextFile(f.file_id, f.name, f.content, new_parent_id)


def change_file_content(f: TextFile, new_content: str) -> TextFile:
    if new_content == "":
        return f

    return TextFile(f.file_id, f.name, new_content, f.parent_id)


def destroy_file(f: TextFile) -> RemovedFile:
    return RemovedFile(f.file_id)
