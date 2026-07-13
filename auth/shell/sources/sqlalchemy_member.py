from dataclasses import dataclass
import sqlalchemy as sa
from result import Err, Result, is_err


from database.database import engine, metadata
from ...member import *

sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("username", sa.String(255), nullable=False, unique=True),
    sa.Column("password", sa.String(255), nullable=False, unique=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)


def fetch_member_by_username(username: str) -> Result[Member, str]:
    query = sa.text(
        "SELECT id, username, password FROM users WHERE username = :username"
    )

    with engine.connect() as conn:
        result = conn.execute(query, {"username": username})
        row = result.mappings().first()

        if row is None:
            return Err("user not found")

        return new_member(row["username"], row["password"])


def save_candidate(cnd: Candidate) -> Result[Member, str]:
    try:
        with engine.connect() as conn:
            query = sa.text(
                "INSERT INTO users (username, password) VAlUES (:username, :password)"
            )
            conn.execute(
                query,
                {
                    "username": cnd.username,
                    "password": cnd.password_hash,
                },
            )
            conn.commit()

            return new_member(cnd.username, cnd.password_hash)
    except sa.exc.IntegrityError as e:
        if e.orig and len(e.orig.args) > 0 and e.orig.args[0] == 1062:
            return Err("user is exists")
        raise


def fetch_all_members() -> list[Member]:
    query = sa.text("SELECT username, password FROM users")

    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()

        out: list[Member] = []
        for row in rows:
            m = new_member(str(row["username"]), str(row["password"]))
            if not is_err(m):
                out.append(m.unwrap())

        return out
