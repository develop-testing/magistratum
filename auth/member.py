from __future__ import annotations
from dataclasses import dataclass

import bcrypt


@dataclass(frozen=True, slots=True)
class Member:
    username: str
    password_hash: str


def new_member(uname: str, hash: str) -> Member:
    if len(uname) > 255:
        raise ValueError("incorrect username length")

    if len(hash) > 255:
        raise ValueError("incorrect password hash")

    return Member(username=uname, password_hash=hash)


def is_password_incorect(member: Member, password: str) -> Member:
    if not bcrypt.checkpw(password.encode(), member.password_hash.encode()):
        raise PermissionError("incorrect password")

    return member


@dataclass(frozen=True, slots=True)
class Candidate:
    username: str
    password_hash: str


def new_candidate(uname: str, password_hash: str) -> Candidate:

    if len(uname) > 255:
        raise ValueError("incorrect username length")

    return Candidate(username=uname, password_hash=password_hash)


def make_candidate(uname: str, password: str) -> Candidate:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return new_candidate(uname=uname, password_hash=hashed.decode())
