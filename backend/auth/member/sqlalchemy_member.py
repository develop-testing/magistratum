from dataclasses import dataclass
import sqlalchemy as sa
from sqlalchemy.engine import Connection


from backend.database.database import metadata
from . import member as mbr

sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("username", sa.String(255), nullable=False, unique=True),
    sa.Column("password", sa.String(255), nullable=False, unique=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)


class DeleteError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def fetch_member_by_username(conn: Connection, username: str) -> mbr.Member:
    query = sa.text(
        "SELECT id, username, password FROM users WHERE username = :username"
    )

    result = conn.execute(query, {"username": username})
    row = result.mappings().first()

    if row is None:
        raise ValueError("user not found")

    return mbr.new_member(row["username"], row["password"])


def fetch_member_profile_by_username(conn: Connection, username: str) -> mbr.MemberProfile:
    query = sa.text(
        "SELECT id, username, password FROM users WHERE username = :username"
    )

    result = conn.execute(query, {"username": username})
    row = result.mappings().first()

    if row is None:
        raise ValueError("user not found")

    return mbr.mk_member_profile(str(row["username"]))


def save_candidate(conn: Connection, cnd: mbr.Candidate) -> Connection:
    try:
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

        return conn
    except sa.exc.IntegrityError as e:
        if e.orig and len(e.orig.args) > 0 and e.orig.args[0] == 1062:
            raise ValueError("user is exists")
        raise


def fetch_all_members(conn: Connection) -> list[mbr.Member]:
    query = sa.text("SELECT username, password FROM users")

    rows = conn.execute(query).mappings().all()

    out: list[mbr.Member] = []
    for row in rows:
        m = mbr.new_member(str(row["username"]), str(row["password"]))
        out.append(m)

    return out


def fetch_all_profiles(conn: Connection) -> list[mbr.MemberProfile]:
    query = sa.text("SELECT username, password FROM users")

    rows = conn.execute(query).mappings().all()

    out: list[mbr.MemberProfile] = []
    for row in rows:
        m = mbr.mk_member_profile(str(row["username"]))
        out.append(m)

    return out


def fetch_members_by_filter(
    conn: Connection, fltr: mbr.FilterOfMember
) -> list[mbr.MemberProfile]:
    if fltr.by_name:
        return [fetch_member_profile_by_username(conn, fltr.by_name)]

    return fetch_all_profiles(conn)


def delete_member_by_username(conn: Connection, username: str) -> Connection:
    query = sa.text("DELETE FROM users WHERE username = :username")

    result = conn.execute(query, {"username": username})

    if result.rowcount == 0:
        raise DeleteError("user not found")

    return conn
