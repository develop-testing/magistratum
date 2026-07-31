from __future__ import annotations

import re

MAX_LEN = 255
MAX_CONTENT_LEN = 65535

NAME_RE = re.compile(r"^[\w\-. ]+$")
USERNAME_RE = re.compile(r"^[\w.-]+$")
PERMISSIONS_RE = re.compile(r"^[rwx-]{4}$")
SRC_RE = re.compile(
    r"^/public/(upload/[0-9a-f]{32}\.(png|jpg)|img/not-found\.png)$"
)
CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
CONTENT_BLOCKED_RE = re.compile(
    r"<\s*/?\s*(script|iframe|object|embed)|"
    r"(javascript|vbscript)\s*:|data\s*:\s*text/html|"
    r"\s+on[a-z]+\s*=|expression\s*\(",
    re.IGNORECASE,
)


def validate_id(value: str) -> None:
    if value == "" or len(value) > MAX_LEN:
        raise ValueError("invalid id")


def validate_name(value: str) -> None:
    if value == "" or len(value) > MAX_LEN:
        raise ValueError("invalid name")
    if value != value.strip():
        raise ValueError("invalid name")
    if not NAME_RE.match(value):
        raise ValueError("invalid name")


def validate_username(value: str) -> None:
    if value == "" or len(value) > MAX_LEN:
        raise ValueError("invalid username")
    if not USERNAME_RE.match(value):
        raise ValueError("invalid username")


def validate_permissions(value: str) -> None:
    if not PERMISSIONS_RE.match(value):
        raise ValueError("invalid permissions")


def validate_src(value: str) -> None:
    if not SRC_RE.match(value):
        raise ValueError("invalid image source")


def validate_content(value: str) -> None:
    if len(value) > MAX_CONTENT_LEN:
        raise ValueError("content is too long")
    if CTRL_RE.search(value):
        raise ValueError("invalid content")
    if CONTENT_BLOCKED_RE.search(value):
        raise ValueError("invalid content")
