from dataclasses import dataclass
import sqlalchemy as sa
from result import Ok, Err, Result

from database.database import engine

from .text_file import TextFile, TextFileFilter
from .permissions.permissions import Permissions


@dataclass(frozen=True, slots=True)
class SaveFileError:
    value: str


@dataclass(frozen=True, slots=True)
class FetchFileError:
    value: str


def fetch_file_by_name(name: str) -> Result[TextFile, FetchFileError]:
    query = sa.text("SELECT file_id, name, content FROM files WHERE name = :name")

    with engine.connect() as conn:
        row = conn.execute(query, {"name": name}).mappings().first()

        if row is None:
            return Err(FetchFileError("file not found"))

        return Ok(TextFile(str(row["file_id"]), row["name"], row["content"]))


def fetch_file_by_filter(filter: TextFileFilter) -> list[TextFile]:
    limit = filter.limit if filter.limit > 0 else 18446744073709551615
    offset = max(filter.offset, 0)
    pagination = " LIMIT :limit OFFSET :offset"

    with engine.connect() as conn:
        if filter.by_name and filter.by_directory:
            query = sa.text(
                "SELECT f.file_id, f.name, f.content FROM files f"
                " JOIN files_to_dirs ftd ON f.name = ftd.file_id"
                " WHERE f.name = :name AND ftd.dir_id = :dir" + pagination
            )
            rows = (
                conn.execute(
                    query,
                    {
                        "name": filter.by_name,
                        "dir": filter.by_directory,
                        "limit": limit,
                        "offset": offset,
                    },
                )
                .mappings()
                .all()
            )

        elif filter.by_name:
            query = sa.text(
                "SELECT file_id, name, content FROM files WHERE name = :name"
                + pagination
            )
            rows = (
                conn.execute(
                    query, {"name": filter.by_name, "limit": limit, "offset": offset}
                )
                .mappings()
                .all()
            )

        elif filter.by_directory:
            query = sa.text(
                "SELECT f.file_id, f.name, f.content FROM files f"
                " JOIN files_to_dirs ftd ON f.file_id = ftd.file_id"
                " WHERE ftd.dir_id = :dir" + pagination
            )
            rows = (
                conn.execute(
                    query,
                    {"dir": filter.by_directory, "limit": limit, "offset": offset},
                )
                .mappings()
                .all()
            )

        else:
            rows = []

        return [
            TextFile(str(row["file_id"]), row["name"], row["content"]) for row in rows
        ]


def update_file(old_name: str, file: TextFile) -> Result[TextFile, SaveFileError]:
    query = sa.text(
        "UPDATE files SET content = :content, name = :new_name WHERE name = :old_name"
    )
    with engine.connect() as conn:
        conn.execute(
            query,
            {"content": file.content, "new_name": file.name, "old_name": old_name},
        )
        conn.commit()

        return Ok(file)


def save_file(file: TextFile, perms: Permissions) -> Result[TextFile, SaveFileError]:
    try:
        insert_file_query = sa.text(
            "INSERT INTO files (file_id, name, content) VALUES (:file_id, :name, :content)"
        )

        insert_perms_query = sa.text(
            "INSERT INTO permissions (item_id, owner_id, group_name, content) VALUES (:item_id, :owner_id, :group_name, :content)"
        )

        with engine.connect() as conn:
            conn.execute(
                insert_file_query,
                {
                    "file_id": file.file_id,
                    "name": file.name,
                    "content": file.content,
                },
            )

            conn.execute(
                insert_perms_query,
                {
                    "item_id": perms.item_id,
                    "owner_id": perms.owner_id,
                    "group_name": perms.group_name,
                    "content": perms.content,
                },
            )

            conn.commit()

            return Ok(TextFile(file.file_id, file.name, file.content))
    except sa.exc.IntegrityError as e:
        if e.orig and len(e.orig.args) > 0 and e.orig.args[0] == 1062:
            return Err(SaveFileError("file with this name is exists"))
        raise


def delete_file_by_id(file_id: str) -> bool:
    query = sa.text("DELETE FROM files WHERE file_id = :file_id")

    with engine.connect() as conn:
        conn.execute(query, {"file_id": file_id})
        conn.commit()

        return True
