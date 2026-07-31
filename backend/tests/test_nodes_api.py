from __future__ import annotations

from collections.abc import Callable

import pytest

from backend.tests.api_client import (
    Cleanup,
    api_delete,
    api_get,
    api_patch,
    api_post,
    dict_from,
    ids,
    login_headers,
    sub,
    text,
    unique_name,
)

pytestmark = pytest.mark.functional


def _create_dir(
    base_url: str,
    headers: dict[str, str],
    cleanup: Cleanup,
    group: str,
    name: str,
    permissions: str,
) -> str:
    res = api_post(
        base_url,
        "/node/directory",
        headers,
        {
            "name": name,
            "owner": "root",
            "group": group,
            "permissions": permissions,
            "parent_id": "",
        },
    )
    assert res.status == 200
    node_id = text(dict_from(res), "id")
    cleanup.add_node(node_id, headers)
    return node_id


def _create_file(
    base_url: str,
    headers: dict[str, str],
    cleanup: Cleanup,
    group: str,
    name: str,
    parent_id: str,
) -> str:
    res = api_post(
        base_url,
        "/node/text_file",
        headers,
        {
            "name": name,
            "content": "hello world",
            "parent_id": parent_id,
            "owner": "root",
            "group": group,
            "permissions": "rwr-",
        },
    )
    assert res.status == 200
    node_id = text(dict_from(res), "id")
    cleanup.add_node(node_id, headers)
    return node_id


def test_node_lifecycle(
    base_url: str, root_headers: dict[str, str], cleanup: Cleanup
) -> None:
    dir_id = _create_dir(
        base_url,
        root_headers,
        cleanup,
        "root",
        unique_name("ftest_dir"),
        "rwr-",
    )
    file_id = _create_file(
        base_url,
        root_headers,
        cleanup,
        "root",
        unique_name("ftest_file"),
        dir_id,
    )

    root_nodes = api_get(base_url, "/nodes", root_headers, {"parent_id": "root"})
    assert root_nodes.status == 200
    assert dir_id in ids(root_nodes)

    file_res = api_get(base_url, f"/node/{file_id}", root_headers)
    assert file_res.status == 200
    value = sub(dict_from(file_res), "value")
    content = sub(value, "content")
    assert text(content, "content") == "hello world"

    rich = api_get(base_url, f"/node/{file_id}", root_headers, {"data_type": "rich"})
    assert rich.status == 200
    rich_content = sub(sub(dict_from(rich), "value"), "content")
    assert text(sub(rich_content, "decor"), "cover") == "/public/img/not-found.png"
    assert text(sub(rich_content, "file"), "content") == "hello world"

    new_file_name = unique_name("ftest_file2")
    renamed = api_patch(
        base_url,
        f"/node/text_file/{file_id}",
        root_headers,
        {
            "node_id": file_id,
            "new_name": new_file_name,
            "new_content": "updated",
        },
    )
    assert renamed.status == 200
    renamed_content = sub(sub(dict_from(renamed), "value"), "content")
    assert text(renamed_content, "name") == new_file_name
    assert text(renamed_content, "content") == "updated"

    new_dir_name = unique_name("ftest_dir2")
    renamed_dir = api_patch(
        base_url,
        f"/node/directory/{dir_id}",
        root_headers,
        {"node_id": dir_id, "new_name": new_dir_name},
    )
    assert renamed_dir.status == 200
    assert (
        text(sub(sub(dict_from(renamed_dir), "value"), "content"), "name")
        == new_dir_name
    )

    assert api_delete_body(base_url, f"/node/{file_id}", root_headers)
    assert api_delete_body(base_url, f"/node/{dir_id}", root_headers)

    root_nodes = api_get(base_url, "/nodes", root_headers, {"parent_id": "root"})
    assert dir_id not in ids(root_nodes)


def test_text_file_requires_parent(base_url: str, root_headers: dict[str, str]) -> None:
    res = api_post(
        base_url,
        "/node/text_file",
        root_headers,
        {
            "name": unique_name("ftest_file"),
            "content": "x",
            "parent_id": "",
            "owner": "root",
            "group": "root",
            "permissions": "rwr-",
        },
    )
    assert res.status == 400


def test_create_directory_invalid_name(
    base_url: str, root_headers: dict[str, str]
) -> None:
    res = api_post(
        base_url,
        "/node/directory",
        root_headers,
        {
            "name": "bad<name>",
            "owner": "root",
            "group": "root",
            "permissions": "rwr-",
            "parent_id": "",
        },
    )
    assert res.status == 400


def test_create_directory_invalid_permissions(
    base_url: str, root_headers: dict[str, str]
) -> None:
    res = api_post(
        base_url,
        "/node/directory",
        root_headers,
        {
            "name": unique_name("ftest_dir"),
            "owner": "root",
            "group": "root",
            "permissions": "abcd",
            "parent_id": "",
        },
    )
    assert res.status == 400


def test_node_permissions(
    base_url: str,
    root_headers: dict[str, str],
    cleanup: Cleanup,
    register: Callable[[str], str],
) -> None:
    member = register("ftest_mem")
    member_headers = login_headers(base_url, member, "pass123")
    outsider = register("ftest_out")
    outsider_headers = login_headers(base_url, outsider, "pass123")

    group = unique_name("ftest_dev")
    gres = api_post(
        base_url,
        "/group",
        root_headers,
        {"name": group, "owner": "root", "members": [member]},
    )
    assert gres.status == 200
    cleanup.add_group(group, root_headers)

    dir_id = _create_dir(
        base_url, root_headers, cleanup, group, unique_name("ftest_d1"), "rw--"
    )

    assert api_get(base_url, f"/node/{dir_id}", member_headers).status == 200

    rename = api_patch(
        base_url,
        f"/node/directory/{dir_id}",
        member_headers,
        {"node_id": dir_id, "new_name": unique_name("ftest_d1n")},
    )
    assert rename.status == 200

    assert api_get(base_url, f"/node/{dir_id}", outsider_headers).status == 403
    assert dir_id not in ids(
        api_get(base_url, "/nodes", outsider_headers, {"parent_id": "root"})
    )

    revoke = api_patch(
        base_url,
        f"/node/directory/{dir_id}",
        root_headers,
        {"node_id": dir_id, "new_permissions": "r---"},
    )
    assert revoke.status == 200

    denied = api_patch(
        base_url,
        f"/node/directory/{dir_id}",
        member_headers,
        {"node_id": dir_id, "new_name": unique_name("ftest_d1r")},
    )
    assert denied.status == 403


def test_permissions_cascade_to_children(
    base_url: str,
    root_headers: dict[str, str],
    cleanup: Cleanup,
    register: Callable[[str], str],
) -> None:
    member = register("ftest_cm")
    group = unique_name("ftest_cg")
    gres = api_post(
        base_url,
        "/group",
        root_headers,
        {"name": group, "owner": "root", "members": [member]},
    )
    assert gres.status == 200
    cleanup.add_group(group, root_headers)

    dir_id = _create_dir(
        base_url, root_headers, cleanup, group, unique_name("ftest_cd"), "rwr-"
    )
    file_id = _create_file(
        base_url, root_headers, cleanup, group, unique_name("ftest_cf"), dir_id
    )

    updated = api_patch(
        base_url,
        f"/node/directory/{dir_id}",
        root_headers,
        {
            "node_id": dir_id,
            "new_owner": member,
            "new_group": group,
            "new_permissions": "rw--",
        },
    )
    assert updated.status == 200

    file_res = api_get(base_url, f"/node/{file_id}", root_headers)
    assert file_res.status == 200
    perms = sub(dict_from(file_res), "permitions")
    assert text(perms, "owner") == member
    assert text(perms, "group") == group
    assert text(perms, "permitions") == "rw--"


def api_delete_body(base_url: str, path: str, headers: dict[str, str]) -> bool:
    res = api_delete(base_url, path, headers, None)
    return res.status == 200 and res.body is True
