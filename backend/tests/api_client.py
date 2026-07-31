from __future__ import annotations

import re
import uuid
from collections.abc import Callable
from dataclasses import dataclass

import requests

LOGIN_TOKEN_RE = re.compile(r"access_token=([^;]+)")


@dataclass(frozen=True, slots=True)
class HttpResult:
    status: int
    body: object


def unique_name(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def login_headers(base_url: str, username: str, password: str) -> dict[str, str]:
    resp = requests.post(
        f"{base_url}/auth/login",
        json={"username": username, "password": password},
        timeout=10,
    )
    if resp.status_code != 200:
        raise ValueError(f"login failed: {resp.status_code} {resp.text}")
    match = LOGIN_TOKEN_RE.search(resp.headers.get("set-cookie", ""))
    if match is None:
        raise ValueError("no access_token in set-cookie")
    return {"Cookie": f"access_token={match.group(1)}"}


def api_get(
    base_url: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, str] | None = None,
) -> HttpResult:
    resp = requests.get(f"{base_url}{path}", params=params, headers=headers, timeout=10)
    return HttpResult(resp.status_code, _body(resp))


def api_post(
    base_url: str, path: str, headers: dict[str, str], body: object
) -> HttpResult:
    resp = requests.post(f"{base_url}{path}", json=body, headers=headers, timeout=10)
    return HttpResult(resp.status_code, _body(resp))


def api_patch(
    base_url: str, path: str, headers: dict[str, str], body: object
) -> HttpResult:
    resp = requests.patch(f"{base_url}{path}", json=body, headers=headers, timeout=10)
    return HttpResult(resp.status_code, _body(resp))


def api_delete(
    base_url: str, path: str, headers: dict[str, str], body: object
) -> HttpResult:
    resp = requests.delete(f"{base_url}{path}", json=body, headers=headers, timeout=10)
    return HttpResult(resp.status_code, _body(resp))


def _body(resp: requests.Response) -> object:
    try:
        return resp.json()
    except ValueError:
        return resp.text


def dict_from(res: HttpResult) -> dict[str, object]:
    if not isinstance(res.body, dict):
        raise AssertionError(f"expected dict body, got {type(res.body)}")
    return res.body


def list_from(res: HttpResult) -> list[object]:
    if not isinstance(res.body, list):
        raise AssertionError(f"expected list body, got {type(res.body)}")
    return res.body


def sub(data: dict[str, object], key: str) -> dict[str, object]:
    value = data[key]
    if not isinstance(value, dict):
        raise AssertionError(f"expected dict at {key}, got {type(value)}")
    return value


def text(data: dict[str, object], key: str) -> str:
    value = data[key]
    if not isinstance(value, str):
        raise AssertionError(f"expected str at {key}, got {type(value)}")
    return value


def ids(res: HttpResult) -> list[str]:
    out: list[str] = []
    for item in list_from(res):
        if isinstance(item, dict):
            value = item.get("id")
            if isinstance(value, str):
                out.append(value)
    return out


class Cleanup:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self._jobs: list[Callable[[], None]] = []

    def add(self, job: Callable[[], None]) -> None:
        self._jobs.append(job)

    def add_user(self, username: str, headers: dict[str, str]) -> None:
        def job() -> None:
            api_delete(self._base_url, "/group", headers, {"name": username})
            api_delete(self._base_url, "/members/", headers, {"username": username})

        self.add(job)

    def add_group(self, name: str, headers: dict[str, str]) -> None:
        def job() -> None:
            api_delete(self._base_url, "/group", headers, {"name": name})

        self.add(job)

    def add_node(self, node_id: str, headers: dict[str, str]) -> None:
        def job() -> None:
            api_delete(self._base_url, f"/node/{node_id}", headers, None)

        self.add(job)

    def run(self) -> None:
        for job in reversed(self._jobs):
            try:
                job()
            except Exception:
                pass
