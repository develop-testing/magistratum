from __future__ import annotations

from time import time

import pytest

from backend.auth.session import session as ssn


def test_mk_session() -> None:
    session = ssn.mk_session("0" * 64, "aleksey", 12345)
    assert session.id == "0" * 64
    assert session.owner == "aleksey"
    assert session.expires == 12345


def test_mk_session_rejects_bad_id() -> None:
    with pytest.raises(ValueError):
        ssn.mk_session("short", "aleksey", 12345)


def test_mk_session_rejects_long_owner() -> None:
    with pytest.raises(ValueError):
        ssn.mk_session("0" * 64, "x" * 251, 12345)


def test_mk_session_rejects_big_expires() -> None:
    with pytest.raises(ValueError):
        ssn.mk_session("0" * 64, "aleksey", 100000000000)


def test_make_session() -> None:
    session = ssn.make_session("aleksey", "0" * 64)
    assert session.owner == "aleksey"
    assert session.expires > int(time())


def test_close_session() -> None:
    session = ssn.make_session("aleksey", "0" * 64)
    closed = ssn.close_session(session)
    assert closed.id == session.id
    assert closed.owner == session.owner
    assert closed.expires == -1


def test_generate_session_for() -> None:
    session = ssn.generate_session_for("aleksey")
    assert len(session.id) == 64
    assert all(c in "0123456789abcdef" for c in session.id)
