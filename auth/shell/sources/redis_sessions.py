from __future__ import annotations


from database.redis import client
from ...session import *


def fetch_session_by_id(session_id: str) -> Session:
    if client.exists(session_id):
        owner_id = client.get(session_id)
        return session_of(session_id, str(owner_id), client.ttl(session_id))

    raise ValueError("session not found")


def save_session(ssn: Session) -> Session:
    client.set(ssn.id, ssn.owner, ex=ssn.expires)
    return ssn
