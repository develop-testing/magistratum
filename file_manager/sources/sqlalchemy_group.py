import sqlalchemy as sa
from result import Err, Ok, Result

from database.database import engine, metadata

from ..groups import Group

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

        members_data = [
            {"username": username, "group_id": id} for username in grp.members
        ]

        if members_data:
            conn.execute(members_query, members_data)

        conn.commit()

    return grp


def fetch_group_by_name(name: str) -> Result[Group, str]:
    query = sa.text("SELECT id, name, owner_name FROM groups WHERE name = :name")

    members_query = sa.text(
        "SELECT username FROM users_to_groups WHERE group_id = CAST(:group_id AS VARCHAR)"
    )

    with engine.connect() as conn:
        row = conn.execute(query, {"name": name}).mappings().first()

        if row is None:
            return Err("group not found")

        members = [
            row2[0] for row2 in conn.execute(members_query, {"group_id": row["id"]})
        ]

        return Ok(Group(row["name"], row["owner_name"], members))


def update_group(old_name: str, group: Group) -> Result[Group, str]:
    id_query = sa.text(
        "UPDATE groups SET name = :new_name, owner_name = :owner_name WHERE name = :old_name RETURNING id"
    )

    delete_members_query = sa.text(
        "DELETE FROM users_to_groups WHERE group_id = :group_id"
    )

    insert_members_query = sa.text(
        "INSERT INTO users_to_groups (username, group_id) VALUES (:username, :group_id)"
    )

    with engine.connect() as conn:
        group_id = conn.execute(
            id_query,
            {"new_name": group.name, "owner_name": group.owner, "old_name": old_name},
        ).scalar()

        if group_id is None:
            return Err("group not found")

        conn.execute(delete_members_query, {"group_id": group_id})

        for username in group.members:
            conn.execute(
                insert_members_query,
                {"username": username, "group_id": group_id},
            )

        conn.commit()

        return Ok(group)


def delete_group_by_name(name: str) -> None:
    id_query = sa.text("SELECT id FROM groups WHERE name = :name")

    delete_members_query = sa.text(
        "DELETE FROM users_to_groups WHERE group_id = CAST(:group_id AS VARCHAR)"
    )

    delete_group_query = sa.text("DELETE FROM groups WHERE name = :name")

    with engine.connect() as conn:
        row = conn.execute(id_query, {"name": name}).mappings().first()
        if row is None:
            return

        conn.execute(delete_members_query, {"group_id": row["id"]})
        conn.execute(delete_group_query, {"name": name})
        conn.commit()


def fetch_groups_by_user(username: str) -> list[Group]:
    groups_query = sa.text("""
        SELECT g.id, g.name, g.owner_name
        FROM groups g
        JOIN users_to_groups utg ON g.id = CAST(utg.group_id AS INTEGER)
        WHERE utg.username = :username
    """)

    members_query = sa.text("""
        SELECT username FROM users_to_groups WHERE group_id = CAST(:group_id AS VARCHAR)
    """)

    with engine.connect() as conn:
        group_rows = conn.execute(groups_query, {"username": username}).mappings().all()

        groups: list[Group] = []
        for row in group_rows:
            members = [
                row2[0] for row2 in conn.execute(members_query, {"group_id": row["id"]})
            ]
            groups.append(Group(row["name"], row["owner_name"], members))

    return groups
