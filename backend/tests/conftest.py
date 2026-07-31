from __future__ import annotations

import os
from collections.abc import Callable, Iterator

import pytest

from backend.tests.api_client import (
    Cleanup,
    api_post,
    login_headers,
    unique_name,
)

BASE_URL = os.environ.get("FUNC_BASE_URL", "http://backend:8000")


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def root_headers(base_url: str) -> Iterator[dict[str, str]]:
    headers = login_headers(base_url, "root", "root")
    yield headers
    api_post(base_url, "/auth/logout", headers, None)


@pytest.fixture()
def cleanup(base_url: str) -> Iterator[Cleanup]:
    items = Cleanup(base_url)
    yield items
    items.run()


@pytest.fixture()
def register(
    base_url: str, root_headers: dict[str, str], cleanup: Cleanup
) -> Callable[[str], str]:
    def _register(prefix: str) -> str:
        username = unique_name(prefix)
        res = api_post(
            base_url,
            "/auth/register",
            {},
            {"username": username, "password": "pass123"},
        )
        if res.status != 200:
            raise AssertionError(f"register failed: {res.status} {res.body}")
        cleanup.add_user(username, root_headers)
        return username

    return _register
