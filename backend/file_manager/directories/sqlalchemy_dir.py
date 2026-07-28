from dataclasses import dataclass
import sqlalchemy as sa

from backend.database.database import engine, metadata


from .directory import *
from ..permissions.permissions import *
from ..permissions.sqlalchemy_permissions import fetch_permissions_for


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
    sa.Column("parent_id", sa.String(255), nullable=False, unique=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)

sa.Table(
    "dirs_to_image",
    metadata,
    sa.Column("dir_id", sa.String(255), nullable=False, unique=True, primary_key=True),
    sa.Column("image_path", sa.String(500), nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
)


def fetch_all_dirs() -> list[Directory]:
    query = sa.text("SELECT dir_id, name, parent_id FROM directories")

    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
        return [
            Directory(str(r["dir_id"]), str(r["name"]), str(r["parent_id"]), [])
            for r in rows
        ]


def fetch_dirs_by_parent(parent_id: str) -> list[Directory]:
    query = sa.text(
        "SELECT dir_id, name, parent_id FROM directories WHERE parent_id = :parent_id"
    )

    with engine.connect() as conn:
        rows = conn.execute(query, {"parent_id": parent_id}).mappings().all()

        if not rows:
            return []

        return [
            mk_directory(row["dir_id"], row["name"], row["parent_id"], [])
            for row in rows
        ]


def fetch_dir_by_id(dir_id: str) -> Directory:
    query = sa.text(
        "SELECT dir_id, name, parent_id FROM directories WHERE dir_id = :dir_id"
    )

    with engine.connect() as conn:
        row = conn.execute(query, {"dir_id": dir_id}).mappings().first()

        if row is None:
            raise DirFetchError("directory not found")

        return Directory(row["dir_id"], row["name"], row["parent_id"], [])


def fetch_dir_by_name(dirname: str) -> Directory:
    query = sa.text(
        "SELECT dir_id, name, parent_id FROM directories WHERE name = :dirname"
    )

    with engine.connect() as conn:
        result = conn.execute(query, {"dirname": dirname})
        row = result.mappings().first()

        if row is None:
            raise DirFetchError("directory not found")

        return Directory(row["dir_id"], row["name"], row["parent_id"], [])


def fetch_dirs_by_filter(fltr: DirFilter) -> list[Directory]:
    if fltr.by_id:
        return [fetch_dir_by_id(fltr.by_id)]

    if fltr.by_name:
        return [fetch_dir_by_name(fltr.by_name)]

    if fltr.parent_id:
        return fetch_dirs_by_parent(fltr.parent_id)

    return fetch_all_dirs()


def fetch_rich_dirs_by_filter(fltr: DirFilter) -> list[RichDirectory]:
    dirs = fetch_dirs_by_filter(fltr)

    if not dirs:
        return []

    prms = fetch_permissions_for([d.dir_id for d in dirs])

    out: list[RichDirectory] = []

    for d in dirs:
        prm = next((p for p in prms if p.item_id == d.dir_id), None)

        if prm is None:
            continue

        image = fetch_image_by_dir(d.dir_id)

        out.append(
            mk_rich_directory(
                d,
                DirPerms.create(
                    prm.owner_name,
                    prm.group_name,
                    group_access(prm),
                    other_access(prm),
                ),
                image,
            )
        )

    return out


def update_directory(d: Directory) -> Directory:
    query = sa.text(
        "UPDATE directories SET name = :name, parent_id = :parent_id WHERE dir_id = :dir_id"
    )

    with engine.connect() as conn:
        conn.execute(
            query,
            {
                "name": d.name,
                "parent_id": d.parent_id,
                "dir_id": d.dir_id,
            },
        )
        conn.commit()

        return d


def save_directory(dir: Directory) -> Directory:
    print(dir)

    query = sa.text(
        "INSERT INTO directories (dir_id, name, parent_id) VALUES (:dir_id, :name, :parent_id)"
    )

    with engine.connect() as conn:
        conn.execute(
            query,
            {
                "dir_id": dir.dir_id,
                "name": dir.name,
                "parent_id": dir.parent_id,
            },
        )
        conn.commit()

        return dir


def delete_directory(dir_id: str) -> bool:
    query = sa.text("DELETE FROM directories WHERE dir_id = :dir_id")

    with engine.connect() as conn:
        conn.execute(query, {"dir_id": dir_id})
        conn.commit()
        return True


def is_dir_exists(dirname: str) -> bool:
    query = sa.text("SELECT EXISTS(SELECT 1 FROM directories WHERE name = :dirname)")

    with engine.connect() as conn:
        return bool(conn.execute(query, {"dirname": dirname}).scalar())


def fetch_image_by_dir(dir_id: str) -> str:
    query = sa.text("SELECT image_path FROM dirs_to_image WHERE dir_id = :dir_id")

    with engine.connect() as conn:
        row = conn.execute(query, {"dir_id": dir_id}).mappings().first()

        if row is None:
            return "/public/img/not-found.png"

        return str(row["image_path"])


def add_image_to_dir(dir_id: str, image_path: str) -> str:
    query = sa.text(
        "INSERT INTO dirs_to_image (dir_id, image_path) VALUES (:dir_id, :image_path)"
        " ON DUPLICATE KEY UPDATE image_path = :image_path"
    )

    try:
        with engine.connect() as conn:
            conn.execute(query, {"dir_id": dir_id, "image_path": image_path})
            conn.commit()
            return image_path
    except sa.exc.IntegrityError:
        raise RuntimeError("failed to save image")
