from __future__ import annotations

import pytest

from backend.image import image as img


def test_new_image() -> None:
    image = img.new_image("/public/img/not-found.png")
    assert image.id != ""
    assert image.src == "/public/img/not-found.png"


def test_mk_image() -> None:
    image = img.mk_image("img-1", "/public/img/not-found.png")
    assert image.id == "img-1"
    assert image.src == "/public/img/not-found.png"


def test_mk_image_rejects() -> None:
    with pytest.raises(ValueError):
        img.mk_image("", "/public/img/not-found.png")
    with pytest.raises(ValueError):
        img.mk_image("img-1", "/etc/passwd")
