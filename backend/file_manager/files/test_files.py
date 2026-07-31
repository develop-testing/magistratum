from __future__ import annotations

from typing import cast

import pytest

from backend.file_manager.files import files as txt


def test_mk_text_file() -> None:
    file = txt.mk_text_file("notes.txt", "hello")
    assert file.name == "notes.txt"
    assert file.content == "hello"


def test_mk_text_file_rejects() -> None:
    with pytest.raises(ValueError):
        txt.mk_text_file("", "hello")
    with pytest.raises(ValueError):
        txt.mk_text_file("notes.txt", "<script>alert(1)</script>")
    with pytest.raises(ValueError):
        txt.mk_text_file("notes.txt", "x" * 65536)


def test_mk_decoration() -> None:
    decor = txt.mk_decoration("/public/img/not-found.png")
    assert decor.cover == "/public/img/not-found.png"


def test_mk_decoration_rejects() -> None:
    with pytest.raises(ValueError):
        txt.mk_decoration("/etc/passwd")


def test_mk_rich_text_file() -> None:
    file = txt.mk_text_file("notes.txt", "hello")
    decor = txt.mk_decoration("/public/img/not-found.png")
    rich = txt.mk_rich_text_file(file, decor)
    assert rich.file is file
    assert rich.decor is decor


def test_mk_rich_text_file_rejects() -> None:
    file = txt.mk_text_file("notes.txt", "hello")
    decor = txt.mk_decoration("/public/img/not-found.png")
    with pytest.raises(ValueError):
        txt.mk_rich_text_file(cast(txt.TextFile, "not a file"), decor)
    with pytest.raises(ValueError):
        txt.mk_rich_text_file(file, cast(txt.Decoration, "not a decor"))


def test_rename_text_file() -> None:
    file = txt.mk_text_file("notes.txt", "hello")
    renamed = txt.rename_text_file(file, "todo.txt")
    assert renamed.name == "todo.txt"
    assert renamed.content == "hello"


def test_rename_text_file_empty_returns_same() -> None:
    file = txt.mk_text_file("notes.txt", "hello")
    assert txt.rename_text_file(file, "") is file


def test_change_text_file_content() -> None:
    file = txt.mk_text_file("notes.txt", "hello")
    changed = txt.change_text_file_content(file, "new text")
    assert changed.name == "notes.txt"
    assert changed.content == "new text"


def test_change_text_file_content_empty_returns_same() -> None:
    file = txt.mk_text_file("notes.txt", "hello")
    assert txt.change_text_file_content(file, "") is file
