from dataclasses import dataclass
import sqlalchemy as sa


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


def fetch_member_by_username(username: str) -> Member:
    query = sa.text(
        "SELECT id, username, password FROM users WHERE username = :username"
    )

    with engine.connect() as conn:
        result = conn.execute(query, {"username": username})
        row = result.mappings().first()

        if row is None:
            raise ValueError("user not found")

        return new_member(row["username"], row["password"])


def fetch_member_profile_by_username(username: str) -> Member:
    query = sa.text(
        "SELECT id, username, password FROM users WHERE username = :username"
    )

    with engine.connect() as conn:
        result = conn.execute(query, {"username": username})
        row = result.mappings().first()

        if row is None:
            raise ValueError("user not found")

        return mk_member_profile(str(row["username"]))


def save_candidate(cnd: Candidate) -> Member:
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
            raise ValueError("user is exists")
        raise


def fetch_all_members() -> list[Member]:
    query = sa.text("SELECT username, password FROM users")

    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()

        out: list[Member] = []
        for row in rows:
            m = new_member(str(row["username"]), str(row["password"]))
            out.append(m)

        return out


def fetch_all_profiles() -> list[Member]:
    query = sa.text("SELECT username, password FROM users")

    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()

        out: list[Member] = []
        for row in rows:
            m = mk_member_profile(str(row["username"]))
            out.append(m)

        return out


def fetch_members_by_filter(fltr: FilterOfMember) -> list[Member]:
    if fltr.by_name:
        return [fetch_member_profile_by_username(fltr.by_name)]

    return fetch_all_profiles()
