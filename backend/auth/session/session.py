from __future__ import annotations
from dataclasses import dataclass
from time import time

import secrets


@dataclass(frozen=True, slots=True)
class Session:
    id: str
    owner: str
    expires: int


def session_of(session_id: str, owner_id: str, expires: int) -> Session:
    if len(owner_id) > 250:
        raise ValueError("owner must be between 3 and 250 characters")

    if not (len(session_id) == 64 and all(c in "0123456789abcdef" for c in session_id)):
        raise ValueError("id must be a 64-character hex string")

    if expires > 99999999999:
        raise ValueError("expires must be less than 999999999")

    return Session(session_id, owner_id, expires)


def make_session(owner: str, session_id: str) -> Session:
    return session_of(session_id, owner, int(time() + 86400))


def close_session(session: Session) -> Session:
    return Session(session.id, session.owner, -1)


def generate_session_for(user_id: str) -> Session:
    if not user_id:
        raise ValueError("username is empty")

    return make_session(user_id, secrets.token_hex(32))
