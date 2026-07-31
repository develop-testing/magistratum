from __future__ import annotations

from typing import cast

import pytest

from backend.file_manager.files import files as txt
from backend.file_manager.directories import directory as dirs


def test_mk_directory() -> None:
    directory = dirs.mk_directory("work")
    assert directory.name == "work"


def test_mk_directory_rejects() -> None:
    with pytest.raises(ValueError):
        dirs.mk_directory("")
    with pytest.raises(ValueError):
        dirs.mk_directory("a<b>")


def test_mk_rich_directory() -> None:
    directory = dirs.mk_directory("work")
    decor = txt.mk_decoration("/public/img/not-found.png")
    rich = dirs.mk_rich_directory(directory, decor)
    assert rich.directory is directory
    assert rich.decor is decor


def test_mk_rich_directory_rejects() -> None:
    directory = dirs.mk_directory("work")
    decor = txt.mk_decoration("/public/img/not-found.png")
    with pytest.raises(ValueError):
        dirs.mk_rich_directory(cast(dirs.Directory, "not a dir"), decor)
    with pytest.raises(ValueError):
        dirs.mk_rich_directory(directory, cast(txt.Decoration, "not a decor"))


def test_rename_directory() -> None:
    directory = dirs.mk_directory("work")
    renamed = dirs.rename_directory(directory, "home")
    assert renamed.name == "home"


def test_rename_directory_empty_returns_same() -> None:
    directory = dirs.mk_directory("work")
    assert dirs.rename_directory(directory, "") is directory
