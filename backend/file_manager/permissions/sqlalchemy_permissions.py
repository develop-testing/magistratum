import sqlalchemy as sa

from backend.database.database import engine, metadata

from .permissions import Permissions, new_permissions

sa.Table(
    "dir_permissions",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("item_id", sa.String(255), nullable=False),
    sa.Column("owner_name", sa.String(255), nullable=False),
    sa.Column("group_name", sa.String(255), nullable=False),
    sa.Column("content", sa.String(4), nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    sa.ForeignKeyConstraint(["item_id"], ["directories.dir_id"], ondelete="CASCADE"),
)

sa.Table(
    "file_permissions",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("item_id", sa.String(255), nullable=False),
    sa.Column("owner_name", sa.String(255), nullable=False),
    sa.Column("group_name", sa.String(255), nullable=False),
    sa.Column("content", sa.String(4), nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    sa.ForeignKeyConstraint(["item_id"], ["files.file_id"], ondelete="CASCADE"),
)


def _save(table_name: str, prms: Permissions) -> Permissions:
    query = sa.text(
        f"INSERT INTO {table_name}"
        " (item_id, owner_name, group_name, content)"
        " VALUE (:item_id, :owner_name, :group_name, :content)"
    )

    with engine.connect() as conn:
        conn.execute(
            query,
            {
                "item_id": prms.item_id,
                "owner_name": prms.owner_name,
                "group_name": prms.group_name,
                "content": prms.content,
            },
        )
        conn.commit()

    return prms


def _fetch_for(table_name: str, item_ids: list[str]) -> list[Permissions]:
    if not item_ids:
        return []

    query = sa.text(
        f"SELECT item_id, owner_name, group_name, content"
        f" FROM {table_name}"
        " WHERE item_id IN :item_id"
    )

    with engine.connect() as conn:
        r = conn.execute(query, {"item_id": tuple(item_ids)}).mappings().all()

        out: list[Permissions] = []
        for item in r:
            try:
                prms = new_permissions(
                    str(item["item_id"]),
                    str(item["owner_name"]),
                    str(item["group_name"]),
                    str(item["content"]),
                )
                out.append(prms)
            except ValueError:
                pass

    return out


def _fetch_by_group(table_name: str, group_name: str) -> list[Permissions]:
    query = sa.text(
        f"SELECT item_id, owner_name, group_name, content"
        f" FROM {table_name}"
        " WHERE group_name = :group_name"
    )

    with engine.connect() as conn:
        r = conn.execute(query, {"group_name": group_name}).mappings().all()

        out: list[Permissions] = []
        for item in r:
            try:
                prms = new_permissions(
                    str(item["item_id"]),
                    str(item["owner_name"]),
                    str(item["group_name"]),
                    str(item["content"]),
                )
                out.append(prms)
            except ValueError:
                pass

    return out


def _update(table_name: str, perms: list[Permissions]) -> None:
    query = sa.text(
        f"UPDATE {table_name}"
        " SET owner_name = :owner_name, group_name = :group_name, content = :content"
        " WHERE item_id = :item_id"
    )

    with engine.connect() as conn:
        for p in perms:
            conn.execute(
                query,
                {
                    "item_id": p.item_id,
                    "owner_name": p.owner_name,
                    "group_name": p.group_name,
                    "content": p.content,
                },
            )
        conn.commit()


def save_dir_permissions(prms: Permissions) -> Permissions:
    return _save("dir_permissions", prms)


def save_file_permissions(prms: Permissions) -> Permissions:
    return _save("file_permissions", prms)


def fetch_dir_permissions_for(dir_ids: list[str]) -> list[Permissions]:
    return _fetch_for("dir_permissions", dir_ids)


def fetch_file_permissions_for(file_ids: list[str]) -> list[Permissions]:
    return _fetch_for("file_permissions", file_ids)


def fetch_dir_permissions_by_group(group_name: str) -> list[Permissions]:
    return _fetch_by_group("dir_permissions", group_name)


def fetch_file_permissions_by_group(group_name: str) -> list[Permissions]:
    return _fetch_by_group("file_permissions", group_name)


def update_dir_permissions(perms: list[Permissions]) -> None:
    _update("dir_permissions", perms)


def update_file_permissions(perms: list[Permissions]) -> None:
    _update("file_permissions", perms)
