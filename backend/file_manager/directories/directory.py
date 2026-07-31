from __future__ import annotations
from dataclasses import dataclass

from ..files import files as txt


@dataclass(slots=True)
class Directory:
    name: str


def mk_directory(name: str) -> Directory:
    return Directory(name)


@dataclass(frozen=True, slots=True)
class RichDirectory:
    directory: Directory
    decor: txt.Decoration


def mk_rich_directory(directory: Directory, decor: txt.Decoration) -> RichDirectory:
    return RichDirectory(directory, decor)


def rename_directory(d: Directory, new_name: str) -> Directory:
    if new_name == "":
        return d
    return mk_directory(new_name)
