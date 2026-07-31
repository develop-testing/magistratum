from __future__ import annotations

import pytest

from backend.tests.api_client import (
    Cleanup,
    api_get,
    api_post,
    login_headers,
    unique_name,
)

pytestmark = pytest.mark.functional


def test_unauthorized_without_cookie(base_url: str) -> None:
    res = api_get(base_url, "/nodes", {})
    assert res.status == 401


def test_register_login_logout_lifecycle(
    base_url: str, root_headers: dict[str, str], cleanup: Cleanup
) -> None:
    username = unique_name("ftest_user")
    res = api_post(
        base_url,
        "/auth/register",
        {},
        {"username": username, "password": "pass123"},
    )
    assert res.status == 200
    assert res.body is True
    cleanup.add_user(username, root_headers)

    headers = login_headers(base_url, username, "pass123")

    nodes = api_get(base_url, "/nodes", headers)
    assert nodes.status == 200

    out = api_post(base_url, "/auth/logout", headers, None)
    assert out.status == 200

    after = api_get(base_url, "/nodes", headers)
    assert after.status == 401


def test_register_duplicate_username(
    base_url: str, root_headers: dict[str, str], cleanup: Cleanup
) -> None:
    username = unique_name("ftest_user")
    first = api_post(
        base_url,
        "/auth/register",
        {},
        {"username": username, "password": "pass123"},
    )
    assert first.status == 200
    cleanup.add_user(username, root_headers)

    second = api_post(
        base_url,
        "/auth/register",
        {},
        {"username": username, "password": "pass123"},
    )
    assert second.status == 400


def test_register_invalid_username(base_url: str) -> None:
    res = api_post(
        base_url,
        "/auth/register",
        {},
        {"username": "bad name", "password": "pass123"},
    )
    assert res.status == 400


def test_login_wrong_password(base_url: str) -> None:
    res = api_post(
        base_url,
        "/auth/login",
        {},
        {"username": "root", "password": "wrong-password"},
    )
    assert res.status == 403


def test_login_unknown_user(base_url: str) -> None:
    res = api_post(
        base_url,
        "/auth/login",
        {},
        {"username": "no_such_user", "password": "pass123"},
    )
    assert res.status == 400
