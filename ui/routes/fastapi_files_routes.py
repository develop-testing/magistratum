from __future__ import annotations
import html
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

import sass_embedded
import chevron  # type: ignore[import-untyped]

from router.response import BadRequest
from file_manager.sources.sqlalchemy_file import fetch_file_by_id

ui_files_router = APIRouter()


@ui_files_router.get("/text_file/edit/{file_id}", tags=["Auth"])
async def dashboar_text_file_edit(file_id: str) -> HTMLResponse:
    fl = fetch_file_by_id(file_id).unwrap_or_raise(BadRequest)

    with open("ui/templates/detail_file/text_file.scss", "r", encoding="utf-8") as f:
        scss_content = f.read()

    result = sass_embedded.compile_string(
        scss_content, load_paths=[Path("ui/templates/")]
    )

    data = {
        "title": "Lorice Administratum",
        "styles": result.output,
        "file_id": file_id,
        "file_name": fl.name,
        "file_content": html.unescape(fl.content),
        "parent_id": fl.parent_id,
    }

    with open(
        "ui/templates/detail_file/text_file.mustache",
        "r",
        encoding="utf-8",
    ) as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)


@ui_files_router.get("/text_file/{file_id}", tags=["Auth"])
async def dashboar_text_file(file_id: str) -> HTMLResponse:
    fl = fetch_file_by_id(file_id).unwrap_or_raise(BadRequest)

    with open("ui/templates/detail_file/text_file.scss", "r", encoding="utf-8") as f:
        scss_content = f.read()

    result = sass_embedded.compile_string(
        scss_content, load_paths=[Path("ui/templates/")]
    )

    data = {
        "title": "Lorice Administratum",
        "styles": result.output,
        "file_id": file_id,
        "file_name": fl.name,
        "file_content": fl.content,
        "parent_id": fl.parent_id,
    }

    with open(
        "ui/templates/detail_file/text_file_read.mustache",
        "r",
        encoding="utf-8",
    ) as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)
