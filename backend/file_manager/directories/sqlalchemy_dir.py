from dataclasses import dataclass
import sqlalchemy as sa
from sqlalchemy.engine import Connection as Conn

from backend.database.database import engine, metadata


from .directory import *
from ..permissions.permissions import Permissions, find_permition_in_list
from ..permissions.sqlalchemy_permissions import fetch_dir_permissions_for


@dataclass
class DirFetchError(Exception):
    message: str

    def __post_init__(self) -> None:
        super().__init__(self.message)


sa.Table(
    "directories",
    metadata,
    sa.Column("dir_id", sa.String(255), nullable=False, unique=True, primary_key=True),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("parent_id", sa.String(255), nullable=True, unique=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    sa.ForeignKeyConstraint(["parent_id"], ["directories.dir_id"], ondelete="CASCADE"),
)

sa.Table(
    "dirs_to_image",
    metadata,
    sa.Column("dir_id", sa.String(255), nullable=False, unique=True, primary_key=True),
    sa.Column("image_path", sa.String(500), nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.ForeignKeyConstraint(["dir_id"], ["directories.dir_id"], ondelete="CASCADE"),
)


def fetch_all_dirs(conn: Conn) -> list[Directory]:
    query = sa.text("SELECT dir_id, name, parent_id FROM directories")
    rows = conn.execute(query).mappings().all()
    return [Directory(str(r["dir_id"]), str(r["name"]), r["parent_id"]) for r in rows]


def fetch_dirs_by_parent(conn: Conn, parent_id: str | None) -> list[Directory]:
    if parent_id:
        query = sa.text(
            "SELECT dir_id, name, parent_id FROM directories WHERE parent_id = :parent_id"
        )
        params: dict[str, str] = {"parent_id": parent_id}
    else:
        query = sa.text(
            "SELECT dir_id, name, parent_id FROM directories WHERE parent_id IS NULL"
        )
        params = {}

    rows = conn.execute(query, params).mappings().all()

    if not rows:
        return []

    return [mk_directory(row["dir_id"], row["name"], row["parent_id"]) for row in rows]


def fetch_dir_by_id(conn: Conn, dir_id: str) -> Directory:
    query = sa.text(
        "SELECT dir_id, name, parent_id FROM directories WHERE dir_id = :dir_id"
    )

    row = conn.execute(query, {"dir_id": dir_id}).mappings().first()

    if row is None:
        raise DirFetchError("directory not found")

    return Directory(row["dir_id"], row["name"], row["parent_id"])


def fetch_dir_by_name(conn: Conn, dirname: str) -> Directory:
    query = sa.text(
        "SELECT dir_id, name, parent_id FROM directories WHERE name = :dirname"
    )

    result = conn.execute(query, {"dirname": dirname})
    row = result.mappings().first()

    if row is None:
        raise DirFetchError("directory not found")

    return Directory(row["dir_id"], row["name"], row["parent_id"])


def fetch_dirs_by_filter(conn: Conn, fltr: DirFilter) -> list[Directory]:
    if fltr.by_id:
        return [fetch_dir_by_id(conn, fltr.by_id)]

    if fltr.by_name:
        return [fetch_dir_by_name(conn, fltr.by_name)]

    if fltr.parent_id:
        return fetch_dirs_by_parent(conn, fltr.parent_id)

    return fetch_all_dirs(conn)


def fetch_rich_dirs_by_filter(conn: Conn, fltr: DirFilter) -> list[RichDirectory]:
    dirs = fetch_dirs_by_filter(conn, fltr)

    if not dirs:
        return []

    prms = fetch_dir_permissions_for(conn, [d.dir_id for d in dirs])

    out: list[RichDirectory] = []

    for d in dirs:
        prm = find_permition_in_list(prms, d.dir_id)

        if prm is None:
            continue

        image = fetch_image_by_dir(conn, d.dir_id)

        out.append(mk_rich_directory(d, prm, image))

    return out


def update_directory(conn: Conn, d: Directory) -> Conn:
    query = sa.text(
        "UPDATE directories SET name = :name, parent_id = :parent_id WHERE dir_id = :dir_id"
    )

    conn.execute(
        query,
        {
            "name": d.name,
            "parent_id": d.parent_id or None,
            "dir_id": d.dir_id,
        },
    )

    return conn


def save_directory(conn: Conn, dir: Directory) -> Conn:
    print(dir)

    query = sa.text(
        "INSERT INTO directories (dir_id, name, parent_id) VALUES (:dir_id, :name, :parent_id)"
    )

    conn.execute(
        query,
        {
            "dir_id": dir.dir_id,
            "name": dir.name,
            "parent_id": dir.parent_id or None,
        },
    )

    return conn


def delete_directory(conn: Conn, dir_id: str) -> Conn:
    query = sa.text("DELETE FROM directories WHERE dir_id = :dir_id")

    conn.execute(query, {"dir_id": dir_id})
    return conn


def is_dir_exists(conn: Conn, dirname: str) -> bool:
    query = sa.text("SELECT EXISTS(SELECT 1 FROM directories WHERE name = :dirname)")
    return bool(conn.execute(query, {"dirname": dirname}).scalar())


def fetch_image_by_dir(conn: Conn, dir_id: str) -> str:
    query = sa.text("SELECT image_path FROM dirs_to_image WHERE dir_id = :dir_id")

    row = conn.execute(query, {"dir_id": dir_id}).mappings().first()

    if row is None:
        return "/public/img/not-found.png"

    return str(row["image_path"])


def add_image_to_dir(conn: Conn, dir_id: str, image_path: str) -> Conn:
    query = sa.text(
        "INSERT INTO dirs_to_image (dir_id, image_path) VALUES (:dir_id, :image_path)"
        " ON DUPLICATE KEY UPDATE image_path = :image_path"
    )

    conn.execute(query, {"dir_id": dir_id, "image_path": image_path})
    return conn
