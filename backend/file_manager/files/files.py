from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TextFile:
    name: str
    content: str


def new_text_file(name: str, content: str) -> TextFile:
    return TextFile(name, content)


def rename_text_file(f: TextFile, new_name: str) -> TextFile:
    if new_name == "":
        return f
    return TextFile(new_name, f.content)


def change_text_file_content(f: TextFile, new_content: str) -> TextFile:
    if new_content == "":
        return f
    return TextFile(f.name, new_content)
