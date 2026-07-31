from __future__ import annotations

import pytest

from backend.file_manager.groups import groups as grps


def test_mk_group_prepends_owner() -> None:
    group = grps.mk_group("dev", "root", ["aleksey"])
    assert group.name == "dev"
    assert group.owner == "root"
    assert group.members == ["dev", "aleksey"]


def test_mk_group_keeps_existing_name() -> None:
    group = grps.mk_group("dev", "root", ["dev", "aleksey"])
    assert group.members == ["dev", "aleksey"]


def test_mk_group_rejects() -> None:
    with pytest.raises(ValueError):
        grps.mk_group("", "root", [])
    with pytest.raises(ValueError):
        grps.mk_group("dev", "bad owner", [])
    with pytest.raises(ValueError):
        grps.mk_group("dev", "root", ["bad<member>"])


def test_mk_removed_group() -> None:
    removed = grps.mk_removed_group("dev")
    assert removed.name == "dev"


def test_rename_group() -> None:
    group = grps.mk_group("dev", "root", ["aleksey"])
    renamed = grps.rename_group(group, "prod")
    assert renamed.name == "prod"
    assert renamed.members == ["prod", "dev", "aleksey"]


def test_rename_group_empty_returns_same() -> None:
    group = grps.mk_group("dev", "root", ["aleksey"])
    assert grps.rename_group(group, "") is group


def test_change_owner() -> None:
    group = grps.mk_group("dev", "root", ["aleksey"])
    changed = grps.change_owner(group, "aleksey")
    assert changed.owner == "aleksey"


def test_add_member() -> None:
    group = grps.mk_group("dev", "root", [])
    added = grps.add_member(group, "aleksey")
    assert "aleksey" in added.members


def test_add_member_existing_returns_same() -> None:
    group = grps.mk_group("dev", "root", ["aleksey"])
    assert grps.add_member(group, "aleksey") is group


def test_remove_member() -> None:
    group = grps.mk_group("dev", "root", ["aleksey", "ivan"])
    removed = grps.remove_member(group, "aleksey")
    assert "aleksey" not in removed.members


def test_remove_member_missing_returns_same() -> None:
    group = grps.mk_group("dev", "root", ["aleksey"])
    assert grps.remove_member(group, "ivan") is group


def test_destroy_group() -> None:
    group = grps.mk_group("dev", "root", ["aleksey"])
    removed = grps.destroy_group(group)
    assert removed.name == "dev"


def test_get_group_names() -> None:
    groups = [
        grps.mk_group("dev", "root", []),
        grps.mk_group("prod", "root", []),
    ]
    assert grps.get_group_names(groups) == ["dev", "prod"]
