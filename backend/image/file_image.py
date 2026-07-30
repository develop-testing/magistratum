from __future__ import annotations
from pathlib import Path
import base64
import uuid

UPLOAD_DIR = Path("frontend/public/upload")


def save_image_file(data_url: str) -> str:
    if "," not in data_url:
        raise ValueError("invalid image data")

    header, encoded = data_url.split(",", 1)
    ext = "png"
    if "jpeg" in header or "jpg" in header:
        ext = "jpg"

    try:
        raw = base64.b64decode(encoded)
    except Exception:
        raise ValueError("invalid base64 data")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = UPLOAD_DIR / filename
    file_path.write_bytes(raw)
    return f"/public/upload/{filename}"


def delete_image_file(src: str) -> None:
    if not src:
        return
    file_path = UPLOAD_DIR / Path(src).name
    if file_path.exists():
        file_path.unlink()
