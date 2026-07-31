from __future__ import annotations

from typing import cast

import pytest

from backend.file_manager.directories import directory as dirs
from backend.file_manager.files import files as txt
from backend.file_manager.node import node as nmd


def make_directory_node(permitions: str, group: str = "dev") -> nmd.Node:
    prmts = nmd.mk_node_permitions("aleksey", group, permitions)
    value = nmd.mk_node_value("directory", dirs.mk_directory("docs"))
    return nmd.mk_node("node-1", "parent-1", prmts, value)


def test_mk_node_permitions() -> None:
    prmts = nmd.mk_node_permitions("aleksey", "dev", "rw--")
    assert prmts.owner == "aleksey"
    assert prmts.group == "dev"
    assert prmts.permitions == "rw--"


def test_mk_node_permitions_rejects() -> None:
    with pytest.raises(ValueError):
        nmd.mk_node_permitions("bad name", "dev", "rw--")
    with pytest.raises(ValueError):
        nmd.mk_node_permitions("aleksey", "dev", "rwx")


def test_mk_node_value_directory() -> None:
    value = nmd.mk_node_value("directory", dirs.mk_directory("docs"))
    assert value.type == "directory"


def test_mk_node_value_text_file() -> None:
    value = nmd.mk_node_value("text_file", txt.mk_text_file("notes.txt", "hi"))
    assert value.type == "text_file"


def test_mk_node_value_rejects() -> None:
    with pytest.raises(ValueError):
        nmd.mk_node_value("directory", txt.mk_text_file("notes.txt", "hi"))
    with pytest.raises(ValueError):
        nmd.mk_node_value("text_file", dirs.mk_directory("docs"))
    with pytest.raises(ValueError):
        nmd.mk_node_value("other", dirs.mk_directory("docs"))


def test_new_node() -> None:
    node = nmd.new_node(
        "parent-1",
        nmd.mk_node_permitions("aleksey", "dev", "rw--"),
        nmd.mk_node_value("directory", dirs.mk_directory("docs")),
    )
    assert node.id != ""
    assert node.parent_id == "parent-1"


def test_mk_node() -> None:
    node = nmd.mk_node(
        "node-1",
        "parent-1",
        nmd.mk_node_permitions("aleksey", "dev", "rw--"),
        nmd.mk_node_value("directory", dirs.mk_directory("docs")),
    )
    assert node.id == "node-1"
    assert node.parent_id == "parent-1"


def test_mk_node_empty_parent_allowed() -> None:
    node = nmd.mk_node(
        "node-1",
        "",
        nmd.mk_node_permitions("aleksey", "dev", "rw--"),
        nmd.mk_node_value("directory", dirs.mk_directory("docs")),
    )
    assert node.parent_id == ""


def test_mk_node_rejects() -> None:
    prmts = nmd.mk_node_permitions("aleksey", "dev", "rw--")
    value = nmd.mk_node_value("directory", dirs.mk_directory("docs"))
    with pytest.raises(ValueError):
        nmd.mk_node("", "parent-1", prmts, value)
    with pytest.raises(ValueError):
        nmd.mk_node("node-1", "x" * 256, prmts, value)
    with pytest.raises(ValueError):
        nmd.mk_node("node-1", "parent-1", cast(nmd.NodePermitions, "not perms"), value)
    with pytest.raises(ValueError):
        nmd.mk_node("node-1", "parent-1", prmts, cast(nmd.NodeValue, "not value"))


def test_has_read() -> None:
    node = make_directory_node("rwr-")
    assert nmd.has_read(node, "root", [])
    assert nmd.has_read(node, "aleksey", [])
    assert nmd.has_read(node, "ivan", ["dev"])
    assert nmd.has_read(node, "ivan", [])


def test_has_read_denies_other() -> None:
    node = make_directory_node("--w-")
    assert not nmd.has_read(node, "ivan", [])


def test_has_write() -> None:
    node = make_directory_node("rwr-")
    assert nmd.has_write(node, "root", [])
    assert nmd.has_write(node, "aleksey", [])
    assert nmd.has_write(node, "ivan", ["dev"])


def test_has_write_denies_other() -> None:
    node = make_directory_node("--r-")
    assert not nmd.has_write(node, "ivan", [])
