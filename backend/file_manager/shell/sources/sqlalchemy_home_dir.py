import sqlalchemy as sa

from backend.database.database import engine, metadata

from ...directories.home_directory import HomeDirectory

sa.Table(
    "home_dirs",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("username", sa.String(255), nullable=False, unique=True),
    sa.Column("dir_id", sa.String(255), nullable=False),
)


def fetch_home_dir_by_username(username: str) -> HomeDirectory:
    query = sa.text(
        "SELECT username AS name, dir_id, username AS user_id FROM home_dirs WHERE username = :username"
    )

    with engine.connect() as conn:
        row = conn.execute(query, {"username": username}).mappings().first()

        if row is None:
            raise ValueError("home directory not found")

        return HomeDirectory(row["name"], row["dir_id"], row["user_id"])


def save_home_dir(h: HomeDirectory) -> HomeDirectory:
    query = sa.text(
        "INSERT INTO home_dirs (username, dir_id) VALUES (:username, :dir_id)"
    )

    with engine.connect() as conn:
        conn.execute(query, {"username": h.name, "dir_id": h.dir_id})
        conn.commit()

    return h


def update_home_dir(h: HomeDirectory) -> HomeDirectory:
    query = sa.text("UPDATE home_dirs SET dir_id = :dir_id WHERE username = :username")

    with engine.connect() as conn:
        conn.execute(query, {"dir_id": h.dir_id, "username": h.name})
        conn.commit()

    return h


def delete_home_dir(h: HomeDirectory) -> bool:
    query = sa.text("DELETE FROM home_dirs WHERE username = :username")

    with engine.connect() as conn:
        conn.execute(query, {"username": h.name})
        conn.commit()

    return True
