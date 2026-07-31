from __future__ import annotations

import pytest

from backend.validation import validation as vld


def test_validate_id() -> None:
    vld.validate_id("abc")
    vld.validate_id("x" * 255)


def test_validate_id_rejects() -> None:
    with pytest.raises(ValueError):
        vld.validate_id("")
    with pytest.raises(ValueError):
        vld.validate_id("x" * 256)


def test_validate_name() -> None:
    vld.validate_name("dir")
    vld.validate_name("My Folder 1")
    vld.validate_name("file.txt")


def test_validate_name_rejects() -> None:
    with pytest.raises(ValueError):
        vld.validate_name("")
    with pytest.raises(ValueError):
        vld.validate_name("a<b>")
    with pytest.raises(ValueError):
        vld.validate_name(" name")
    with pytest.raises(ValueError):
        vld.validate_name("x" * 256)


def test_validate_username() -> None:
    vld.validate_username("aleksey")
    vld.validate_username("a.b-c")


def test_validate_username_rejects() -> None:
    with pytest.raises(ValueError):
        vld.validate_username("")
    with pytest.raises(ValueError):
        vld.validate_username("bad name")


def test_validate_permissions() -> None:
    vld.validate_permissions("rw--")
    vld.validate_permissions("rwr-")


def test_validate_permissions_rejects() -> None:
    with pytest.raises(ValueError):
        vld.validate_permissions("rwx")
    with pytest.raises(ValueError):
        vld.validate_permissions("rwa-")


def test_validate_src() -> None:
    vld.validate_src("/public/img/not-found.png")
    vld.validate_src("/public/upload/" + "a" * 32 + ".png")
    vld.validate_src("/public/upload/" + "a" * 32 + ".jpg")


def test_validate_src_rejects() -> None:
    with pytest.raises(ValueError):
        vld.validate_src("")
    with pytest.raises(ValueError):
        vld.validate_src("/etc/passwd")
    with pytest.raises(ValueError):
        vld.validate_src("/public/upload/abc.png")


def test_validate_content() -> None:
    vld.validate_content("plain text")
    vld.validate_content("x" * 65535)


def test_validate_content_rejects() -> None:
    with pytest.raises(ValueError):
        vld.validate_content("<script>alert(1)</script>")
    with pytest.raises(ValueError):
        vld.validate_content("bad\x00content")
    with pytest.raises(ValueError):
        vld.validate_content("x" * 65536)
