from dataclasses import dataclass
import sqlalchemy as sa
from result import Ok, Err, Result, is_err

from database.database import engine, metadata

from ..permissions import PermErrs, Permissions, new_permissions


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
from ..text_file import TextFileFilter


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

def fetch_permissions_for(item_ids: list[str]) -> list[Permissions]:
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
                prms = new_permissions(
                    str(item["item_id"]),
                    str(item["owner_name"]),
                    str(item["group_name"]),
                    str(item["content"])
                )

                if not is_err(prms):
                    out.append(prms.unwrap())


    return out
