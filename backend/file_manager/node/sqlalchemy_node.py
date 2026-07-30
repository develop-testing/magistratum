from __future__ import annotations
from dataclasses import dataclass
import sqlalchemy as sa
from sqlalchemy.engine import Connection as Conn

from backend.database.database import engine, metadata
from .node import Node, NodeFilter, NodePermitions, NodeValue
from ..directories.directory import Directory
from ..files.files import TextFile


sa.Table(
    "nodes",
    metadata,
    sa.Column("id", sa.String(255), primary_key=True),
    sa.Column("parent_id", sa.String(255), sa.ForeignKey("nodes.id", ondelete="CASCADE")),
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
    sa.Column("node_id", sa.String(255), sa.ForeignKey("nodes.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("content", sa.Text, nullable=False),
)

sa.Table(
    "node_directories",
    metadata,
    sa.Column("node_id", sa.String(255), sa.ForeignKey("nodes.id", ondelete="CASCADE"), primary_key=True),
)


@dataclass
class NodeFetchError(Exception):
    message: str

    def __post_init__(self) -> None:
        super().__init__(self.message)


def row_to_node(row: sa.RowMapping) -> Node:
    if row.get("dir_node_id") is not None:
        content: Directory | TextFile = Directory(name=row["name"])
        ntype = "directory"
    else:
        content = TextFile(name=row["name"], content=row.get("content") or "")
        ntype = "text_file"

    return Node(
        id=row["id"],
        parent_id=row["parent_id"] or "",
        permitions=NodePermitions(
            owner=row["owner"],
            group=row["group"],
            permitions=row["permissions"],
        ),
        value=NodeValue(type=ntype, content=content),
    )


def save_node(conn: Conn, node: Node) -> Conn:
    conn.execute(
        sa.text(
            "INSERT INTO nodes (id, parent_id, name, owner, `group`, permissions) "
            "VALUES (:id, :parent_id, :name, :owner, :group, :permissions)"
        ),
        {
            "id": node.id,
            "parent_id": node.parent_id or None,
            "name": node.value.content.name,
            "owner": node.permitions.owner,
            "group": node.permitions.group,
            "permissions": node.permitions.permitions,
        },
    )

    if isinstance(node.value.content, TextFile):
        conn.execute(
            sa.text(
                "INSERT INTO node_text_files (node_id, content) VALUES (:node_id, :content)"
            ),
            {"node_id": node.id, "content": node.value.content.content},
        )
    else:
        conn.execute(
            sa.text(
                "INSERT INTO node_directories (node_id) VALUES (:node_id)"
            ),
            {"node_id": node.id},
        )

    return conn


def fetch_node(conn: Conn, node_id: str) -> Node:
    row = conn.execute(
        sa.text(
            "SELECT n.*, ntf.content, nd.node_id AS dir_node_id "
            "FROM nodes n "
            "LEFT JOIN node_text_files ntf ON n.id = ntf.node_id "
            "LEFT JOIN node_directories nd ON n.id = nd.node_id "
            "WHERE n.id = :id"
        ),
        {"id": node_id},
    ).mappings().first()
    if row is None:
        raise NodeFetchError("node not found")
    return row_to_node(row)


def fetch_nodes(conn: Conn, fltr: NodeFilter = NodeFilter()) -> list[Node]:
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

    rows = conn.execute(
        sa.text(
            "SELECT n.*, ntf.content, nd.node_id AS dir_node_id "
            "FROM nodes n "
            "LEFT JOIN node_text_files ntf ON n.id = ntf.node_id "
            "LEFT JOIN node_directories nd ON n.id = nd.node_id "
            f"{where}"
        ),
        params,
    ).mappings().all()

    return [row_to_node(r) for r in rows]


def update_node(conn: Conn, node: Node) -> Conn:
    conn.execute(
        sa.text(
            "UPDATE nodes SET parent_id = :parent_id, name = :name, "
            "owner = :owner, `group` = :group, permissions = :permissions "
            "WHERE id = :id"
        ),
        {
            "id": node.id,
            "parent_id": node.parent_id or None,
            "name": node.value.content.name,
            "owner": node.permitions.owner,
            "group": node.permitions.group,
            "permissions": node.permitions.permitions,
        },
    )

    if isinstance(node.value.content, TextFile):
        conn.execute(
            sa.text(
                "INSERT INTO node_text_files (node_id, content) "
                "VALUES (:node_id, :content) "
                "ON DUPLICATE KEY UPDATE content = :content"
            ),
            {"node_id": node.id, "content": node.value.content.content},
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


def delete_node(conn: Conn, node_id: str) -> Conn:
    conn.execute(sa.text("DELETE FROM nodes WHERE id = :id"), {"id": node_id})
    return conn
