from __future__ import annotations
from dataclasses import dataclass
from result import Ok, Result


@dataclass(frozen=True, slots=True)
class HomeDirectory:
    name: str
    dir_id: str
    user_id: str


def mk_directory(name: str, dir_id: str, user_id: str) -> Result[HomeDirectory, str]:
    return Ok(HomeDirectory(name, dir_id, user_id))


def change(h: HomeDirectory, dir_id: str, user_id: str) -> Result[HomeDirectory, str]:
    return Ok(HomeDirectory(h.name, dir_id, user_id))
