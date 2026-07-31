from __future__ import annotations
from dataclasses import dataclass
import sqlalchemy as sa
from sqlalchemy.engine import Connection as Conn

from backend.database.database import engine, metadata
from ..directories import directory as dirs
from ..files import files as txt
from . import node as nmd

sa.Table(
    "nodes",
    metadata,
    sa.Column("id", sa.String(255), primary_key=True),
    sa.Column(
        "parent_id",
        sa.String(255),
        sa.ForeignKey("nodes.id", ondelete="CASCADE"),
    ),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("owner", sa.String(255), nullable=False),
    sa.Column("group", sa.String(255), nullable=False),
    sa.Column("permissions", sa.String(4), nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)

sa.Table(
    "node_text_files",
    metadata,
    sa.Column(
        "node_id",
        sa.String(255),
        sa.ForeignKey("nodes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column("content", sa.Text, nullable=False),
)

sa.Table(
    "node_directories",
    metadata,
    sa.Column(
        "node_id",
        sa.String(255),
        sa.ForeignKey("nodes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

sa.Table(
    "file_to_images",
    metadata,
    sa.Column(
        "node_id",
        sa.String(255),
        sa.ForeignKey("nodes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "image_id",
        sa.String(255),
        sa.ForeignKey("images.id", ondelete="CASCADE"),
    ),
)

sa.Table(
    "dir_to_images",
    metadata,
    sa.Column(
        "node_id",
        sa.String(255),
        sa.ForeignKey("nodes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    sa.Column(
        "image_id",
        sa.String(255),
        sa.ForeignKey("images.id", ondelete="CASCADE"),
    ),
)


@dataclass
class NodeFetchError(Exception):
    message: str

    def __post_init__(self) -> None:
        super().__init__(self.message)


def row_to_node(row: sa.RowMapping) -> nmd.Node:
    if row.get("dir_node_id") is not None:
        content: nmd.Values = dirs.new_directory(row["name"])
        ntype = "directory"
    else:
        content = txt.new_text_file(row["name"], row.get("content") or "")
        ntype = "text_file"

    return nmd.mk_node(
        id=row["id"],
        parent_id=row["parent_id"] or "",
        prmts=nmd.new_node_permitions(
            owner=row["owner"],
            group=row["group"],
            permitions=row["permissions"],
        ),
        value=nmd.new_node_value(type=ntype, content=content),
    )


def save_node(conn: Conn, node: nmd.Node) -> Conn:
    content = node.value.content
    if isinstance(content, txt.RichTextFile):
        content = content.file
    elif isinstance(content, dirs.RichDirectory):
        content = content.directory

    conn.execute(
        sa.text(
            "INSERT INTO nodes (id, parent_id, name, owner, `group`, permissions) "
            "VALUES (:id, :parent_id, :name, :owner, :group, :permissions)"
        ),
        {
            "id": node.id,
            "parent_id": node.parent_id or None,
            "name": content.name,
            "owner": node.permitions.owner,
            "group": node.permitions.group,
            "permissions": node.permitions.permitions,
        },
    )

    if isinstance(content, txt.TextFile):
        conn.execute(
            sa.text(
                "INSERT INTO node_text_files (node_id, content) VALUES (:node_id, :content)"
            ),
            {"node_id": node.id, "content": content.content},
        )
    else:
        conn.execute(
            sa.text("INSERT INTO node_directories (node_id) VALUES (:node_id)"),
            {"node_id": node.id},
        )

    return conn


def fetch_node(conn: Conn, node_id: str) -> nmd.Node:
    row = (
        conn.execute(
            sa.text(
                "SELECT n.*, ntf.content, nd.node_id AS dir_node_id "
                "FROM nodes n "
                "LEFT JOIN node_text_files ntf ON n.id = ntf.node_id "
                "LEFT JOIN node_directories nd ON n.id = nd.node_id "
                "WHERE n.id = :id"
            ),
            {"id": node_id},
        )
        .mappings()
        .first()
    )
    if row is None:
        raise NodeFetchError("node not found")
    return row_to_node(row)


def fetch_nodes(conn: Conn, fltr: nmd.NodeFilter = nmd.NodeFilter()) -> list[nmd.Node]:
    conditions = []
    params: dict[str, str] = {}

    if fltr.parent_id == "root":
        conditions.append("n.parent_id IS NULL")
    elif fltr.parent_id:
        conditions.append("n.parent_id = :parent_id")
        params["parent_id"] = fltr.parent_id
    if fltr.type_filter:
        if fltr.type_filter == "directory":
            conditions.append("nd.node_id IS NOT NULL")
        else:
            conditions.append("ntf.node_id IS NOT NULL")

    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    rows = (
        conn.execute(
            sa.text(
                "SELECT n.*, ntf.content, nd.node_id AS dir_node_id "
                "FROM nodes n "
                "LEFT JOIN node_text_files ntf ON n.id = ntf.node_id "
                "LEFT JOIN node_directories nd ON n.id = nd.node_id "
                f"{where}"
            ),
            params,
        )
        .mappings()
        .all()
    )

    return [row_to_node(r) for r in rows]


def update_node(conn: Conn, node: nmd.Node) -> Conn:
    content = node.value.content
    if isinstance(content, txt.RichTextFile):
        content = content.file
    elif isinstance(content, dirs.RichDirectory):
        content = content.directory

    conn.execute(
        sa.text(
            "UPDATE nodes SET parent_id = :parent_id, name = :name, "
            "owner = :owner, `group` = :group, permissions = :permissions "
            "WHERE id = :id"
        ),
        {
            "id": node.id,
            "parent_id": node.parent_id or None,
            "name": content.name,
            "owner": node.permitions.owner,
            "group": node.permitions.group,
            "permissions": node.permitions.permitions,
        },
    )

    if isinstance(content, txt.TextFile):
        conn.execute(
            sa.text(
                "INSERT INTO node_text_files (node_id, content) "
                "VALUES (:node_id, :content) "
                "ON DUPLICATE KEY UPDATE content = :content"
            ),
            {"node_id": node.id, "content": content.content},
        )
    else:
        conn.execute(
            sa.text(
                "INSERT INTO node_directories (node_id) "
                "VALUES (:node_id) "
                "ON DUPLICATE KEY UPDATE node_id = node_id"
            ),
            {"node_id": node.id},
        )

    return conn


def update_perms(
    conn: Conn, node_id: str, owner: str, group: str, permissions: str
) -> Conn:
    conn.execute(
        sa.text("""
            WITH RECURSIVE descendants AS (
                SELECT id FROM nodes WHERE parent_id = :root_id
                UNION ALL
                SELECT n.id FROM nodes n
                JOIN descendants d ON n.parent_id = d.id
            )
            UPDATE nodes
            SET owner = :owner, `group` = :group, permissions = :permissions
            WHERE id IN (SELECT id FROM descendants)
        """),
        {
            "root_id": node_id,
            "owner": owner,
            "group": group,
            "permissions": permissions,
        },
    )
    return conn


def delete_node(conn: Conn, node_id: str) -> Conn:
    conn.execute(sa.text("DELETE FROM nodes WHERE id = :id"), {"id": node_id})
    return conn


def add_image_to_file(conn: Conn, node_id: str, image_id: str) -> Conn:
    conn.execute(
        sa.text(
            "INSERT INTO file_to_images (node_id, image_id) "
            "VALUES (:node_id, :image_id) "
            "ON DUPLICATE KEY UPDATE image_id = :image_id"
        ),
        {"node_id": node_id, "image_id": image_id},
    )
    return conn


def fetch_image_by_file(conn: Conn, node_id: str) -> str | None:
    row = (
        conn.execute(
            sa.text(
                "SELECT i.src FROM file_to_images nti "
                "JOIN images i ON nti.image_id = i.id "
                "WHERE nti.node_id = :node_id"
            ),
            {"node_id": node_id},
        )
        .mappings()
        .first()
    )

    if row is None:
        return None

    return str(row["src"])


def remove_image_from_file(conn: Conn, node_id: str) -> Conn:
    conn.execute(
        sa.text("DELETE FROM file_to_images WHERE node_id = :node_id"),
        {"node_id": node_id},
    )
    return conn


def add_image_to_dir(conn: Conn, node_id: str, image_id: str) -> Conn:
    conn.execute(
        sa.text(
            "INSERT INTO dir_to_images (node_id, image_id) "
            "VALUES (:node_id, :image_id) "
            "ON DUPLICATE KEY UPDATE image_id = :image_id"
        ),
        {"node_id": node_id, "image_id": image_id},
    )
    return conn


def fetch_image_by_dir(conn: Conn, node_id: str) -> str | None:
    row = (
        conn.execute(
            sa.text(
                "SELECT i.src FROM dir_to_images nti "
                "JOIN images i ON nti.image_id = i.id "
                "WHERE nti.node_id = :node_id"
            ),
            {"node_id": node_id},
        )
        .mappings()
        .first()
    )

    if row is None:
        return None

    return str(row["src"])


def remove_image_from_dir(conn: Conn, node_id: str) -> Conn:
    conn.execute(
        sa.text("DELETE FROM dir_to_images WHERE node_id = :node_id"),
        {"node_id": node_id},
    )
    return conn
