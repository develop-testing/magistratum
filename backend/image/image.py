from __future__ import annotations
from dataclasses import dataclass
import uuid


@dataclass(frozen=True, slots=True)
class Image:
    id: str
    src: str


def new_image(src: str) -> Image:
    return Image(id=str(uuid.uuid4()), src=src)


def mk_image(id: str, src: str) -> Image:
    return Image(id, src)
