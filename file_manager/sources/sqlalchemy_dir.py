from dataclasses import dataclass
import sqlalchemy as sa
from result import Ok, Err, Result

from database.database import engine, metadata


from ..directory import Directory, mk_directory

sa.Table(
    "directories",
    metadata,
    sa.Column("dir_id", sa.String(255), nullable=False, unique=True, primary_key=True),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("parent_id", sa.String(255), nullable=False, unique=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)


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


def fetch_dir_by_name(dirname: str) -> Result[Directory, str]:
    query = sa.text(
        "SELECT dir_id, name, parent_id FROM directories WHERE name = :dirname"
    )

    with engine.connect() as conn:
        result = conn.execute(query, {"dirname": dirname})
        row = result.mappings().first()

        if row is None:
            return Err("directory not found")

        return Ok(Directory(row["dir_id"], row["name"], row["parent_id"], []))


def is_dir_exists(dirname: str) -> bool:
    query = sa.text("SELECT EXISTS(SELECT 1 FROM directories WHERE name = :dirname)")

    with engine.connect() as conn:
        return bool(conn.execute(query, {"dirname": dirname}).scalar())
