from __future__ import annotations
from dataclasses import dataclass
from result import Err, Ok, Result


from database.redis import client
from .session import *


@dataclass(frozen=True, slots=True)
class SessionStoreError:
    value: str


SessionStoreErrs = SessionStoreError | SessionValidateErr


def fetch_session_by_id(session_id: str) -> Result[Session, SessionStoreErrs]:
    if client.exists(session_id):
        owner_id = client.get(session_id)
        return session_of(session_id, str(owner_id), client.ttl(session_id))

    return Err(SessionStoreError("session not found"))


def save_session(ssn: Session) -> Session:
    client.set(ssn.id, ssn.owner, ex=ssn.expires)
    return ssn
