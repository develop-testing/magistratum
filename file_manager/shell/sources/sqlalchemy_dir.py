from dataclasses import dataclass
import sqlalchemy as sa

from database.database import engine, metadata


from ...directories.directory import Directory

sa.Table(
    "directories",
    metadata,
    sa.Column("dir_id", sa.String(255), nullable=False, unique=True, primary_key=True),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("parent_id", sa.String(255), nullable=False, unique=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)


def fetch_dirs_by_parent(parent_id: str) -> list[Directory]:
    query = sa.text(
        "SELECT dir_id, name, parent_id FROM directories WHERE parent_id = :parent_id"
    )

    with engine.connect() as conn:
        rows = conn.execute(query, {"parent_id": parent_id}).mappings().all()
        return [
            Directory(row["dir_id"], row["name"], row["parent_id"], []) for row in rows
        ]


def save_directory(dir: Directory) -> Directory:
    query = sa.text(
        "INSERT INTO directories (dir_id, name, parent_id) VALUES (:dir_id, :name, :parent_id)"
    )

    with engine.connect() as conn:
        result = conn.execute(
            query,
            {
                "dir_id": dir.dir_id,
                "name": dir.name,
                "parent_id": dir.parent_id,
            },
        )
        conn.commit()

        return dir


def fetch_dir_by_id(dir_id: str) -> Directory:
    query = sa.text(
        "SELECT dir_id, name, parent_id FROM directories WHERE dir_id = :dir_id"
    )

    with engine.connect() as conn:
        row = conn.execute(query, {"dir_id": dir_id}).mappings().first()

        if row is None:
            raise ValueError("directory not found")

        return Directory(row["dir_id"], row["name"], row["parent_id"], [])


def fetch_dir_by_name(dirname: str) -> Directory:
    query = sa.text(
        "SELECT dir_id, name, parent_id FROM directories WHERE name = :dirname"
    )

    with engine.connect() as conn:
        result = conn.execute(query, {"dirname": dirname})
        row = result.mappings().first()

        if row is None:
            raise ValueError("directory not found")

        return Directory(row["dir_id"], row["name"], row["parent_id"], [])


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


def fetch_all_dirs() -> list[Directory]:
    query = sa.text("SELECT dir_id, name, parent_id FROM directories")

    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
        return [
            Directory(str(r["dir_id"]), str(r["name"]), str(r["parent_id"]), [])
            for r in rows
        ]
