from dataclasses import dataclass
import sqlalchemy as sa
from result import Ok, Err, Result

from database.database import engine

from .file import *

@dataclass(frozen=True, slots=True)
class FetchDirectoryError:
    value: str

@dataclass(frozen=True, slots=True)
class SaveFileError:
    value: str

def fetch_dir_by_name(dirname: str) -> Result[Directory, str]:
    query = sa.text(
        "SELECT name, parent_name FROM directories WHERE name = :dirname"
    )

    with engine.connect() as conn:
        result = conn.execute(query, {"dirname": dirname})
        row = result.mappings().first()

        if row is None:
            return Err(FetchDirectoryError("directory not found"))

        return new_directory(row["name"], row["parent_name"])

def is_dir_exists(dirname: str) -> bool:
    query = sa.text(
        "SELECT EXISTS(SELECT 1 FROM directories WHERE name = :dirname)"
    )

    with engine.connect() as conn:
        return conn.execute(query, {"dirname": dirname}).scalar()

def save_file(file: File) -> Result[File, SaveFileError]:
    try:
        query = sa.text("INSERT INTO files (name, content) VALUES (:name, :content)")

        with engine.connect() as conn:
            conn.execute(
                query,
                {
                    "name": file.name,
                    "content": file.content,
                }
            )

            conn.commit()

            return Ok(file)
    except sa.exc.IntegrityError as e:
        if e.orig and len(e.orig.args) > 0 and e.orig.args[0] == 1062:
            return Err(SaveFileError("file with this name is exists"))
        raise