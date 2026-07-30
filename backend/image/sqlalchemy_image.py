from __future__ import annotations
import sqlalchemy as sa
from sqlalchemy.engine import Connection

from backend.database.database import metadata
from .image import Image
from .file_image import save_image_file, delete_image_file


sa.Table(
    "images",
    metadata,
    sa.Column("id", sa.String(255), primary_key=True),
    sa.Column("src", sa.String(500), nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)


def save_image(conn: Connection, image: Image) -> Connection:
    src = save_image_file(image.src)

    conn.execute(
        sa.text(
            "INSERT INTO images (id, src) VALUES (:id, :src)"
            " ON DUPLICATE KEY UPDATE src = :src"
        ),
        {"id": image.id, "src": src},
    )
    return conn


def fetch_image(conn: Connection, image_id: str) -> Image:
    row = conn.execute(
        sa.text("SELECT id, src FROM images WHERE id = :id"),
        {"id": image_id},
    ).mappings().first()

    if row is None:
        raise ValueError("image not found")

    return Image(id=row["id"], src=row["src"])


def delete_image(conn: Connection, image_id: str) -> Connection:
    row = conn.execute(
        sa.text("SELECT src FROM images WHERE id = :id"),
        {"id": image_id},
    ).mappings().first()

    if row is not None:
        delete_image_file(row["src"])
        conn.execute(
            sa.text("DELETE FROM images WHERE id = :id"),
            {"id": image_id},
        )

    return conn
