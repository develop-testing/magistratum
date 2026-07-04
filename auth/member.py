from __future__ import annotations
from dataclasses import dataclass

import bcrypt
from result import Ok, Err, Result


@dataclass(frozen=True, slots=True)
class ErrorOfIncorrectCreds:
    value: str


@dataclass(frozen=True, slots=True)
class ErrorOfMemberValidate:
    value: str


MemberErr = ErrorOfIncorrectCreds | ErrorOfMemberValidate


@dataclass(frozen=True, slots=True)
class Member:
    username: str
    password_hash: str


def new_member(uname: str, hash: str) -> Result[Member, MemberErr]:
    if len(uname) > 255:
        return Err(ErrorOfMemberValidate("incorrect username length"))

    if len(hash) > 255:
        return Err(ErrorOfMemberValidate("incorrect password hash"))

    return Ok(Member(username=uname, password_hash=hash))


def is_password_incorect(member: Member, password: str) -> Result[Member, MemberErr]:
    if not bcrypt.checkpw(password.encode(), member.password_hash.encode()):
        return Err(ErrorOfMemberValidate("incorrect password hash"))

    return Ok(member)


@dataclass(frozen=True, slots=True)
class Candidate:
    username: str
    password_hash: str


def new_candidate(uname: str, password_hash: str) -> Result[Candidate, MemberErr]:

    if len(uname) > 255:
        return Err(ErrorOfMemberValidate("incorrect username length"))

    return Ok(Candidate(username=uname, password_hash=password_hash))


def make_candidate(uname: str, password: str) -> Result[Candidate, MemberErr]:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return new_candidate(uname=uname, password_hash=hashed.decode())
