from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HomeDirectory:
    name: str
    dir_id: str
    user_id: str


def mk_directory(name: str, dir_id: str, user_id: str) -> HomeDirectory:
    return HomeDirectory(name, dir_id, user_id)


def change(h: HomeDirectory, dir_id: str, user_id: str) -> HomeDirectory:
    return HomeDirectory(h.name, dir_id, user_id)
