from __future__ import annotations
from dataclasses import dataclass
from result import Err, Ok, Result


@dataclass(frozen=True, slots=True)
class Group:
    name: str
    owner: str
    members: list[str]

def mk_group(name: str, owner: str, members: list[str]) -> Result[Group, str]:
    members = [name] + members if name not in members else members 
    return Group(name, owner, members)
