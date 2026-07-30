from __future__ import annotations
from dataclasses import dataclass

from ..files import files as txt


@dataclass(slots=True)
class Directory:
    name: str


def new_directory(name: str) -> Directory:
    return Directory(name)


@dataclass(frozen=True, slots=True)
class RichDirectory:
    directory: Directory
    decor: txt.Decoration


def new_rich_directory(directory: Directory, decor: txt.Decoration) -> RichDirectory:
    return RichDirectory(directory, decor)


def rename_directory(d: Directory, new_name: str) -> Directory:
    if new_name == "":
        return d
    return Directory(new_name)
