from __future__ import annotations
from result import Result


from files.permissions.permissions import (
    Permissions,
    PermissionsFilter,
    new_permissions,
)


def fetch_permissions(filter: PermissionsFilter) -> Result[Permissions, str]:
    return new_permissions(filter.item_id, "test-user", "test-group", "r-r-")


def save_as(p: Permissions, item_id: str) -> Permissions:
    return p
