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
    user_id: str
    username: str
    password_hash: str


def new_member(uid: str, uname: str, pswd: str, hash: str) -> Result[Member, MemberErr]:
    if len(uid) > 255:
        return Err(ErrorOfMemberValidate("incorrect user id"))

    if len(uname) > 255:
        return Err(ErrorOfMemberValidate("incorrect username length"))

    if len(pswd) > 255:
        return Err(ErrorOfMemberValidate("incorrect password length"))

    if not bcrypt.checkpw(pswd.encode(), hash.encode()):
        return Err(ErrorOfIncorrectCreds("incorrect username or password"))

    return Ok(Member(user_id=uid, username=uname, password_hash=hash))


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
