from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TextFile:
    name: str
    content: str

def new_text_file(name: str, content: str) -> TextFile:
    return TextFile(name, content)


@dataclass(frozen=True, slots=True)
class Decoration:
    cover: str


def new_decoration(cover: str) -> Decoration:
    return Decoration(cover)


@dataclass(frozen=True, slots=True)
class RichTextFile:
    file: TextFile
    decor: Decoration

def new_rich_text_file(file: TextFile, decor: Decoration) -> RichTextFile:
    return RichTextFile(file, decor)


def rename_text_file(f: TextFile, new_name: str) -> TextFile:
    if new_name == "": return f

    return TextFile(new_name, f.content)


def change_text_file_content(f: TextFile, new_content: str) -> TextFile:
    if new_content == "": return f

    return TextFile(f.name, new_content)
