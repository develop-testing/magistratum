from dataclasses import dataclass
import sqlalchemy as sa
from result import Ok, Err, Result

from database.database import engine

from ..permissions import PermErrs, Permissions


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
