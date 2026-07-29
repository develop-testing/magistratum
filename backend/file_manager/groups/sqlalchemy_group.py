from collections.abc import Sequence
import sqlalchemy as sa
from sqlalchemy.engine import Connection

from backend.database.database import metadata

from .groups import FetchGroupReq, Group, RemovedGroup
from ..permissions.permissions import Permissions

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


def save_group(conn: Connection, grp: Group) -> Group:
    create_query = sa.text("""
        INSERT INTO groups (name, owner_name)
        VALUES (:name, :owner_name)
    """)

    select_id_query = sa.text("SELECT id FROM groups WHERE name = :name")

    members_query = sa.text("""
        INSERT INTO users_to_groups (username, group_id)
        VALUES (:username, :group_id)
    """)

    conn.execute(create_query, {"name": grp.name, "owner_name": grp.owner})

    group_id = conn.execute(select_id_query, {"name": grp.name}).scalar()

    members_data = [
        {"username": username, "group_id": group_id} for username in grp.members
    ]

    if members_data:
        conn.execute(members_query, members_data)

    return grp


def fetch_group_by_name(conn: Connection, name: str) -> Group:
    query = sa.text("SELECT id, name, owner_name FROM groups WHERE name = :name")

    members_query = sa.text(
        "SELECT username FROM users_to_groups WHERE group_id = CAST(:group_id AS CHAR)"
    )

    row = conn.execute(query, {"name": name}).mappings().first()

    if row is None:
        raise ValueError("group not found")

    members = [row2[0] for row2 in conn.execute(members_query, {"group_id": row["id"]})]

    return Group(row["name"], row["owner_name"], members)


def update_group(conn: Connection, old_name: str, group: Group) -> Group:
    select_id_query = sa.text("SELECT id FROM groups WHERE name = :name")

    update_query = sa.text(
        "UPDATE groups SET name = :new_name, owner_name = :owner_name WHERE name = :old_name"
    )

    delete_members_query = sa.text(
        "DELETE FROM users_to_groups WHERE group_id = :group_id"
    )

    insert_members_query = sa.text(
        "INSERT INTO users_to_groups (username, group_id) VALUES (:username, :group_id)"
    )

    group_id = conn.execute(select_id_query, {"name": old_name}).scalar()

    if group_id is None:
        raise ValueError("group not found")

    conn.execute(
        update_query,
        {"new_name": group.name, "owner_name": group.owner, "old_name": old_name},
    )

    conn.execute(delete_members_query, {"group_id": group_id})

    for username in group.members:
        conn.execute(
            insert_members_query,
            {"username": username, "group_id": group_id},
        )

    return group


def delete_group_by_name(
    conn: Connection, removed: RemovedGroup, perms: list[Permissions]
) -> None:
    id_query = sa.text("SELECT id FROM groups WHERE name = :name")

    delete_members_query = sa.text(
        "DELETE FROM users_to_groups WHERE group_id = CAST(:group_id AS CHAR)"
    )

    delete_group_query = sa.text("DELETE FROM groups WHERE name = :name")

    for table in ("dir_permissions", "file_permissions"):
        update_perms_query = sa.text(
            f"UPDATE {table}"
            " SET owner_name = :owner_name, group_name = :group_name, content = :content"
            " WHERE item_id = :item_id"
        )
        for p in perms:
            conn.execute(
                update_perms_query,
                {
                    "item_id": p.item_id,
                    "owner_name": p.owner_name,
                    "group_name": p.group_name,
                    "content": p.content,
                },
            )

    row = conn.execute(id_query, {"name": removed.name}).mappings().first()
    if row is not None:
        conn.execute(delete_members_query, {"group_id": row["id"]})
        conn.execute(delete_group_query, {"name": removed.name})


def fetch_groups_by_filter(conn: Connection, filter: FetchGroupReq) -> list[Group]:
    sql = """
        SELECT g.id, g.name, g.owner_name, utg.username
        FROM groups g
        LEFT JOIN users_to_groups utg ON g.id = CAST(utg.group_id AS CHAR)
    """

    params = {}

    if filter.owner and filter.member:
        sql += """
            WHERE g.owner_name = :owner
              AND EXISTS (
                  SELECT 1 FROM users_to_groups sub_utg 
                  WHERE g.id = CAST(sub_utg.group_id AS CHAR) AND sub_utg.username = :member
              )
        """
        params = {"owner": filter.owner, "member": filter.member}

    elif filter.owner:
        sql += " WHERE g.owner_name = :owner"
        params = {"owner": filter.owner}

    elif filter.member:
        sql += """
            WHERE EXISTS (
                SELECT 1 FROM users_to_groups sub_utg 
                WHERE g.id = CAST(sub_utg.group_id AS CHAR) AND sub_utg.username = :member
            )
        """
        params = {"member": filter.member}

    rows = conn.execute(sa.text(sql), params).mappings().all()

    groups_dict: dict[tuple[int, str, str], list[str]] = {}
    for row in rows:
        group_key = (row["id"], row["name"], row["owner_name"])
        members_list = groups_dict.setdefault(group_key, [])

        if row["username"]:
            members_list.append(row["username"])

    return [
        Group(name=name, owner=owner, members=members)
        for (g_id, name, owner), members in groups_dict.items()
    ]


def fetch_groups_by_user(conn: Connection, username: str) -> list[Group]:
    groups_query = sa.text("""
        SELECT g.id, g.name, g.owner_name
        FROM groups g
        JOIN users_to_groups utg ON g.id = CAST(utg.group_id AS INTEGER)
        WHERE utg.username = :username
    """)

    members_query = sa.text("""
        SELECT username FROM users_to_groups WHERE group_id = CAST(:group_id AS CHAR)
    """)

    group_rows = conn.execute(groups_query, {"username": username}).mappings().all()

    groups: list[Group] = []
    for row in group_rows:
        members = [
            row2[0] for row2 in conn.execute(members_query, {"group_id": row["id"]})
        ]
        groups.append(Group(row["name"], row["owner_name"], members))

    return groups


def fetch_all_groups(conn: Connection) -> list[str]:
    query = sa.text("SELECT name FROM groups")

    return [str(r["name"]) for r in conn.execute(query).mappings().all()]
