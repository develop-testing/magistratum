from __future__ import annotations
from dataclasses import dataclass

from ...validation import validation as vld


@dataclass(frozen=True, slots=True)
class TextFile:
    name: str
    content: str


def mk_text_file(name: str, content: str) -> TextFile:
    vld.validate_name(name)
    vld.validate_content(content)
    return TextFile(name, content)


@dataclass(frozen=True, slots=True)
class Decoration:
    cover: str


def mk_decoration(cover: str) -> Decoration:
    vld.validate_src(cover)
    return Decoration(cover)


@dataclass(frozen=True, slots=True)
class RichTextFile:
    file: TextFile
    decor: Decoration


def mk_rich_text_file(file: TextFile, decor: Decoration) -> RichTextFile:
    if not isinstance(file, TextFile):
        raise ValueError("invalid text file")
    if not isinstance(decor, Decoration):
        raise ValueError("invalid decoration")
    return RichTextFile(file, decor)


def rename_text_file(f: TextFile, new_name: str) -> TextFile:
    if new_name == "":
        return f

    return mk_text_file(new_name, f.content)


def change_text_file_content(f: TextFile, new_content: str) -> TextFile:
    if new_content == "":
        return f

    return mk_text_file(f.name, new_content)
