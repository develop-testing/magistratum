from __future__ import annotations

from collections.abc import Callable
from typing import cast

import pytest

from backend.tests.api_client import (
    Cleanup,
    HttpResult,
    api_delete,
    api_get,
    api_patch,
    api_post,
    dict_from,
    login_headers,
    list_from,
    text,
    unique_name,
)

pytestmark = pytest.mark.functional


def _find_group(res: HttpResult, name: str) -> bool:
    for item in list_from(res):
        if not isinstance(item, dict):
            continue
        data = cast(dict[str, object], item)
        if text(data, "name") == name:
            return True
    return False


def test_group_lifecycle(
    base_url: str,
    root_headers: dict[str, str],
    cleanup: Cleanup,
    register: Callable[[str], str],
) -> None:
    member1 = register("ftest_m1")
    member2 = register("ftest_m2")

    name = unique_name("ftest_grp")
    new_name = unique_name("ftest_grp2")
    created = api_post(
        base_url,
        "/group",
        root_headers,
        {"name": name, "owner": "root", "members": [member1]},
    )
    assert created.status == 200
    data = dict_from(created)
    assert text(data, "name") == name
    assert text(data, "owner") == "root"
    cleanup.add_group(name, root_headers)

    seen = api_get(
        base_url, "/groups", root_headers, {"owner": "root", "member": member1}
    )
    assert seen.status == 200
    assert _find_group(seen, name)

    edited = api_patch(
        base_url,
        "/group",
        root_headers,
        {
            "name": name,
            "new_name": new_name,
            "new_owner": member1,
            "new_members": [member1, member2],
        },
    )
    assert edited.status == 200
    data = dict_from(edited)
    assert text(data, "name") == new_name
    assert text(data, "owner") == member1
    cleanup.add_group(new_name, root_headers)

    members = data["members"]
    assert isinstance(members, list)
    assert member1 in members
    assert member2 in members

    seen = api_get(
        base_url, "/groups", root_headers, {"owner": member1, "member": member1}
    )
    assert _find_group(seen, new_name)

    deleted = api_delete(base_url, "/group", root_headers, {"name": new_name})
    assert deleted.status == 200
    assert deleted.body is True

    seen = api_get(
        base_url, "/groups", root_headers, {"owner": member1, "member": member1}
    )
    assert not _find_group(seen, new_name)


def test_create_group_forbidden_for_non_root(
    base_url: str, cleanup: Cleanup, register: Callable[[str], str]
) -> None:
    username = register("ftest_grp")
    headers = login_headers(base_url, username, "pass123")
    res = api_post(
        base_url,
        "/group",
        headers,
        {"name": unique_name("ftest_grp"), "owner": username, "members": []},
    )
    assert res.status == 403


def test_edit_and_delete_group_forbidden_for_non_owner(
    base_url: str,
    root_headers: dict[str, str],
    cleanup: Cleanup,
    register: Callable[[str], str],
) -> None:
    owner = register("ftest_owner")
    outsider = register("ftest_out")
    outsider_headers = login_headers(base_url, outsider, "pass123")

    name = unique_name("ftest_grp")
    created = api_post(
        base_url,
        "/group",
        root_headers,
        {"name": name, "owner": owner, "members": [owner]},
    )
    assert created.status == 200
    cleanup.add_group(name, root_headers)

    edited = api_patch(
        base_url,
        "/group",
        outsider_headers,
        {
            "name": name,
            "new_name": unique_name("ftest_grp2"),
            "new_owner": owner,
            "new_members": [owner],
        },
    )
    assert edited.status == 403

    deleted = api_delete(base_url, "/group", outsider_headers, {"name": name})
    assert deleted.status == 403
