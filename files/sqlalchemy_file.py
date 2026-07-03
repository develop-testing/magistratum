from dataclasses import dataclass
import sqlalchemy as sa
from result import Ok, Err, Result

from database.database import engine

from .text_file import TextFile, RemovedFile, TextFileFilter
from .directory import Directory, new_directory


@dataclass(frozen=True, slots=True)
class FetchDirectoryError:
    value: str


@dataclass(frozen=True, slots=True)
class SaveFileError:
    value: str


@dataclass(frozen=True, slots=True)
class FetchFileError:
    value: str


FetchFileErrs = FetchDirectoryError | str


def fetch_dir_by_name(dirname: str) -> Result[Directory, FetchFileErrs]:
    query = sa.text("SELECT name, parent_name FROM directories WHERE name = :dirname")

    with engine.connect() as conn:
        result = conn.execute(query, {"dirname": dirname})
        row = result.mappings().first()

        if row is None:
            return Err(FetchDirectoryError("directory not found"))

        return new_directory(row["name"], row["parent_name"])


def is_dir_exists(dirname: str) -> bool:
    query = sa.text("SELECT EXISTS(SELECT 1 FROM directories WHERE name = :dirname)")

    with engine.connect() as conn:
        return bool(conn.execute(query, {"dirname": dirname}).scalar())


def fetch_file_by_name(name: str) -> Result[TextFile, FetchFileError]:
    query = sa.text("SELECT name, content FROM files WHERE name = :name")

    with engine.connect() as conn:
        row = conn.execute(query, {"name": name}).mappings().first()

        if row is None:
            return Err(FetchFileError("file not found"))

        return Ok(TextFile(row["name"], row["content"]))


def fetch_file_by_filter(filter: TextFileFilter) -> list[TextFile]:
    limit = filter.limit if filter.limit > 0 else 18446744073709551615
    offset = max(filter.offset, 0)
    pagination = " LIMIT :limit OFFSET :offset"

    with engine.connect() as conn:
        if filter.by_name and filter.by_directory:
            query = sa.text(
                "SELECT f.name, f.content FROM files f"
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
                "SELECT name, content FROM files WHERE name = :name" + pagination
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
                "SELECT f.name, f.content FROM files f"
                " JOIN files_to_dirs ftd ON f.name = ftd.file_id"
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

        return [TextFile(row["name"], row["content"]) for row in rows]


def update_file(old_name: str, file: TextFile) -> Result[TextFile, SaveFileError]:
    try:
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
    except sa.exc.IntegrityError as e:
        if e.orig and len(e.orig.args) > 0 and e.orig.args[0] == 1062:
            return Err(SaveFileError("file with this name already exists"))
        raise


def save_file(file: TextFile) -> Result[TextFile, SaveFileError]:
    try:
        query = sa.text("INSERT INTO files (name, content) VALUES (:name, :content)")

        with engine.connect() as conn:
            conn.execute(
                query,
                {
                    "name": file.name,
                    "content": file.content,
                },
            )

            conn.commit()

            return Ok(file)
    except sa.exc.IntegrityError as e:
        if e.orig and len(e.orig.args) > 0 and e.orig.args[0] == 1062:
            return Err(SaveFileError("file with this name is exists"))
        raise

def delete_file_by_name(file_name: str) -> bool:
    query = sa.text("DELETE FROM files WHERE name = :name")

    with engine.connect() as conn:
        conn.execute(query, {"name": file_name})
        conn.commit()

        return True
