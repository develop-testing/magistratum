from __future__ import annotations
from dataclasses import dataclass
import uuid

from ..validation import validation as vld


@dataclass(frozen=True, slots=True)
class Image:
    id: str
    src: str


def new_image(src: str) -> Image:
    return mk_image(id=str(uuid.uuid4()), src=src)


def mk_image(id: str, src: str) -> Image:
    vld.validate_id(id)
    vld.validate_src(src)
    return Image(id, src)
