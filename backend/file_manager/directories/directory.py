from __future__ import annotations
from dataclasses import dataclass


@dataclass(slots=True)
class Directory:
    name: str


def new_directory(name: str) -> Directory:
    return Directory(name)


def rename_directory(d: Directory, new_name: str) -> Directory:
    if new_name == "":
        return d
    return Directory(new_name)
