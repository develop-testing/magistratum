from __future__ import annotations

import pytest

from backend.auth.member import member as mb


def test_mk_member() -> None:
    member = mb.mk_member("aleksey", "hash123")
    assert member.username == "aleksey"
    assert member.password_hash == "hash123"


def test_mk_member_rejects_bad_username() -> None:
    with pytest.raises(ValueError):
        mb.mk_member("bad name", "hash123")


def test_mk_member_rejects_long_hash() -> None:
    with pytest.raises(ValueError):
        mb.mk_member("aleksey", "x" * 256)


def test_mk_candidate() -> None:
    candidate = mb.mk_candidate("aleksey", "hash123")
    assert candidate.username == "aleksey"
    assert candidate.password_hash == "hash123"


def test_make_candidate() -> None:
    candidate = mb.make_candidate("aleksey", "secret")
    assert candidate.username == "aleksey"
    assert candidate.password_hash != "secret"


def test_is_password_incorect() -> None:
    candidate = mb.make_candidate("aleksey", "secret")
    member = mb.mk_member(candidate.username, candidate.password_hash)
    assert mb.is_password_incorect(member, "secret") is member


def test_is_password_incorect_rejects() -> None:
    candidate = mb.make_candidate("aleksey", "secret")
    member = mb.mk_member(candidate.username, candidate.password_hash)
    with pytest.raises(PermissionError):
        mb.is_password_incorect(member, "wrong")


def test_mk_member_profile() -> None:
    profile = mb.mk_member_profile("aleksey")
    assert profile.username == "aleksey"


def test_mk_member_profile_rejects() -> None:
    with pytest.raises(ValueError):
        mb.mk_member_profile("bad name")
