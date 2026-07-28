import sqlalchemy as sa

from backend.database.database import engine, metadata

from .permissions import Permissions, new_permissions

sa.Table(
    "permissions",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("item_id", sa.String(255), nullable=False),
    sa.Column("owner_name", sa.String(255), nullable=False),
    sa.Column("group_name", sa.String(255), nullable=False),
    sa.Column("content", sa.String(4), nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)


def save_permissions(prms: Permissions) -> Permissions:
    query = sa.text("""
        INSERT INTO permissions (item_id, owner_name, group_name, content)
        VALUE (:item_id, :owner_name, :group_name, :content)
    """)

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


def fetch_permissions_by_group(group_name: str) -> list[Permissions]:
    query = sa.text("""
        SELECT item_id, owner_name, group_name, content
        FROM permissions
        WHERE group_name = :group_name
    """)

    with engine.connect() as conn:
        r = conn.execute(query, {"group_name": group_name}).mappings().all()

        out = []
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


def update_permissions(perms: list[Permissions]) -> None:
    query = sa.text("""
        UPDATE permissions
        SET owner_name = :owner_name, group_name = :group_name, content = :content
        WHERE item_id = :item_id
    """)

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


def fetch_permissions_for(item_ids: list[str]) -> list[Permissions]:
    if not item_ids:
        return []

    query = sa.text("""
        SELECT item_id, owner_name, group_name, content
        FROM permissions
        WHERE item_id IN :item_id
    """)

    with engine.connect() as conn:
        r = conn.execute(query, {"item_id": tuple(item_ids)}).mappings().all()

        out = []

        if r is not None:
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
