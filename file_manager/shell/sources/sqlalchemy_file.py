from dataclasses import dataclass
import sqlalchemy as sa

from database.database import engine, metadata

from ...files import TextFile, TextFileFilter, mk_text_file

from ...permissions import Permissions

sa.Table(
    "files",
    metadata,
    sa.Column("file_id", sa.String(255), nullable=False, unique=True, primary_key=True),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("content", sa.Text, nullable=False, unique=False),
    sa.Column("parent_id", sa.String(255), nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)

sa.Table(
    "files_to_image",
    metadata,
    sa.Column("file_id", sa.String(255), nullable=False, unique=True, primary_key=True),
    sa.Column("image_path", sa.String(500), nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
)


def fetch_file_by_id(file_id: str) -> TextFile:
    query = sa.text(
        "SELECT file_id, name, content, parent_id FROM files WHERE file_id = :file_id"
    )

    with engine.connect() as conn:
        row = conn.execute(query, {"file_id": file_id}).mappings().first()

        if row is None:
            raise ValueError("file not found")

        return mk_text_file(
            str(row["file_id"]), row["name"], row["content"], str(row["parent_id"])
        )


def fetch_file_by_name(name: str) -> TextFile:
    query = sa.text(
        "SELECT file_id, name, content, parent_id FROM files WHERE name = :name"
    )

    with engine.connect() as conn:
        row = conn.execute(query, {"name": name}).mappings().first()

        if row is None:
            raise ValueError("file not found")

        return mk_text_file(
            str(row["file_id"]), row["name"], row["content"], str(row["parent_id"])
        )


def fetch_file_by_filter(filter: TextFileFilter) -> list[TextFile]:
    limit = filter.limit if filter.limit > 0 else 18446744073709551615
    offset = max(filter.offset, 0)
    pagination = " LIMIT :limit OFFSET :offset"

    with engine.connect() as conn:
        if filter.by_name and filter.by_directory:
            query = sa.text(
                "SELECT file_id, name, content, parent_id FROM files"
                " WHERE name = :name AND parent_id = :dir" + pagination
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
                "SELECT file_id, name, content, parent_id FROM files WHERE name = :name"
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
                "SELECT file_id, name, content, parent_id FROM files WHERE parent_id = :dir"
                + pagination
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
            mk_text_file(
                str(row["file_id"]), row["name"], row["content"], str(row["parent_id"])
            )
            for row in rows
        ]


def update_file(old_name: str, file: TextFile) -> TextFile:
    query = sa.text(
        "UPDATE files SET content = :content, name = :new_name WHERE name = :old_name"
    )
    with engine.connect() as conn:
        conn.execute(
            query,
            {"content": file.content, "new_name": file.name, "old_name": old_name},
        )
        conn.commit()

        return file


def update_file_by_id(file_id: str, file: TextFile) -> TextFile:
    query = sa.text(
        "UPDATE files SET content = :content, name = :name WHERE file_id = :file_id"
    )
    with engine.connect() as conn:
        conn.execute(
            query,
            {"content": file.content, "name": file.name, "file_id": file_id},
        )
        conn.commit()
        return file


def save_file(file: TextFile, perms: Permissions) -> TextFile:
    try:
        insert_file_query = sa.text(
            "INSERT INTO files (file_id, name, content, parent_id) VALUES (:file_id, :name, :content, :parent_id)"
        )

        insert_perms_query = sa.text(
            "INSERT INTO permissions (item_id, owner_name, group_name, content) VALUES (:item_id, :owner_name, :group_name, :content)"
        )

        with engine.connect() as conn:
            conn.execute(
                insert_file_query,
                {
                    "file_id": file.file_id,
                    "name": file.name,
                    "content": file.content,
                    "parent_id": file.parent_id,
                },
            )

            conn.execute(
                insert_perms_query,
                {
                    "item_id": perms.item_id,
                    "owner_name": perms.owner_name,
                    "group_name": perms.group_name,
                    "content": perms.content,
                },
            )

            conn.commit()

            return mk_text_file(file.file_id, file.name, file.content, file.parent_id)
    except sa.exc.IntegrityError as e:
        if e.orig and len(e.orig.args) > 0 and e.orig.args[0] == 1062:
            raise ValueError("file with this name is exists")
        raise


def move_file(file_id: str, new_dir_id: str) -> str:
    query = sa.text("UPDATE files SET parent_id = :dir_id WHERE file_id = :file_id")

    with engine.connect() as conn:
        conn.execute(query, {"file_id": file_id, "dir_id": new_dir_id})
        conn.commit()
        return file_id


def delete_file_by_id(file_id: str) -> bool:
    query = sa.text("DELETE FROM files WHERE file_id = :file_id")

    with engine.connect() as conn:
        conn.execute(query, {"file_id": file_id})
        conn.commit()

        return True


def add_image_to_file(file_id: str, image_path: str) -> str:
    query = sa.text(
        "INSERT INTO files_to_image (file_id, image_path) VALUES (:file_id, :image_path)"
        " ON DUPLICATE KEY UPDATE image_path = :image_path"
    )

    try:
        with engine.connect() as conn:
            conn.execute(query, {"file_id": file_id, "image_path": image_path})
            conn.commit()
            return image_path
    except sa.exc.IntegrityError:
        raise RuntimeError("failed to save image")


def fetch_image_by_file(file_id: str) -> str:
    query = sa.text("SELECT image_path FROM files_to_image WHERE file_id = :file_id")

    with engine.connect() as conn:
        row = conn.execute(query, {"file_id": file_id}).mappings().first()

        if row is None:
            raise ValueError("no image")

        return str(row["image_path"])
