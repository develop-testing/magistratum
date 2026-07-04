from dataclasses import dataclass
import sqlalchemy as sa
from result import Ok, Err, Result

from database.database import engine, metadata

from ..groups import Group, mk_group


sa.Table(
    "groups",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String(255), nullable=False, unique=True),
    sa.Column("owner_name", sa.String(255), nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)

sa.Table(
    "users_to_groups",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("username", sa.String(255), nullable=False),
    sa.Column("group_id", sa.String(255), nullable=False),
)


def save_group(grp: Group) -> Group:
    create_query = sa.text("""
        INSERT INTO groups (name, owner_name) 
        VALUES (:name, :owner_name)
        RETURNING id
    """)

    members_query = sa.text("""
        INSERT INTO users_to_groups (username, group_id) 
        VALUES (:username, :group_id)
    """)

    with engine.connect() as conn:
        result = conn.execute(create_query, {"name": grp.name, "owner_name": grp.owner})

        id = result.scalar()

        members_data = [{"username": username, "group_id": id} for username in grp.members]

        if members_data:
            conn.execute(members_query, members_data)

        conn.commit()

    return grp
