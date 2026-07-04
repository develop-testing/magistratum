from dataclasses import dataclass
import sqlalchemy as sa
from result import Ok, Err, Result


from database.database import engine
from ..member import *


@dataclass(frozen=True, slots=True)
class SaveDuplicateError:
    value: str


@dataclass(frozen=True, slots=True)
class NotFoundMemberError:
    value: str


MemberErrors = SaveDuplicateError | NotFoundMemberError | MemberErr


def fetch_member_by_username(username: str) -> Result[Member, MemberErrors]:
    query = sa.text(
        "SELECT id, username, password FROM users WHERE username = :username"
    )

    with engine.connect() as conn:
        result = conn.execute(query, {"username": username})
        row = result.mappings().first()

        if row is None:
            return Err(NotFoundMemberError("user not found"))

        return new_member(row["username"], row["password"])


def save_candidate(cnd: Candidate) -> Result[Member, MemberErrors]:
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
            return Err(SaveDuplicateError("user is exists"))
        raise
