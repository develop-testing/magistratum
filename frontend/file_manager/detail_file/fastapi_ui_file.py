from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

import sass_embedded
import chevron  # type: ignore[import-untyped]

ui_files_router = APIRouter()

layout = "frontend/common.mustache"

tiny_mce_head = (
    '<link rel="stylesheet" '
    'href="/static/file_manager/detail_file/tinymce/skins/ui/oxide/skin.min.css">'
)


def _compile_styles() -> str:
    scss_file = "frontend/file_manager/detail_file/text_file.scss"

    with open(scss_file, "r", encoding="utf-8") as f:
        scss_content = f.read()

    return sass_embedded.compile_string(
        scss_content,
        load_paths=[
            Path("frontend/file_manager/detail_file/"),
            Path("frontend/"),
        ],
    ).output


@ui_files_router.get("/text_file/edit/{file_id}", tags=["Auth"])
async def dashboar_text_file_edit(req: Request, file_id: str) -> HTMLResponse:
    session_owner = req.state.session.owner
    template = "frontend/file_manager/detail_file/text_file.mustache"
    styles = _compile_styles()

    with open(template, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl, {"editor": session_owner})

    with open(layout, "r", encoding="utf-8") as f:
        html_content = chevron.render(f, {
            "title": "Lorice Administratum",
            "styles": styles,
            "content": tmpl_content,
            "extra_head": tiny_mce_head,
        })

    return HTMLResponse(html_content)


@ui_files_router.get("/text_file/{file_id}", tags=["Auth"])
async def dashboar_text_file(file_id: str) -> HTMLResponse:
    template = "frontend/file_manager/detail_file/text_file_read.mustache"
    styles = _compile_styles()

    with open(template, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl)

    with open(layout, "r", encoding="utf-8") as f:
        html_content = chevron.render(f, {
            "title": "Lorice Administratum",
            "styles": styles,
            "content": tmpl_content,
        })

    return HTMLResponse(html_content)
