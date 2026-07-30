from __future__ import annotations


from backend.database.redis import client
from . import session as ssn_src


def fetch_session_by_id(session_id: str) -> ssn_src.Session:
    if client.exists(session_id):
        owner_id = client.get(session_id)
        return ssn_src.session_of(session_id, str(owner_id), client.ttl(session_id))

    raise ValueError("session not found")


def save_session(ssn: ssn_src.Session) -> ssn_src.Session:
    client.set(ssn.id, ssn.owner, ex=ssn.expires)
    return ssn


def close_session(ssn: ssn_src.Session) -> None:
    client.delete(ssn.id)
