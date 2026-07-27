from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

import chevron  # type: ignore[import-untyped]

from mustache_default import generate_layout

ui_files_router = APIRouter()


@ui_files_router.get("/text_file/edit/{file_id}", tags=["Auth"])
async def dashboar_text_file_edit(req: Request, file_id: str) -> HTMLResponse:
    session_owner = req.state.session.owner
    template = "frontend/file_manager/detail_file/text_file.mustache"

    with open(template, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl, {"editor": session_owner})

    return HTMLResponse(generate_layout(tmpl_content, session_owner))


@ui_files_router.get("/text_file/{file_id}", tags=["Auth"])
async def dashboar_text_file(file_id: str) -> HTMLResponse:
    template = "frontend/file_manager/detail_file/text_file_read.mustache"

    with open(template, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl)

    return HTMLResponse(generate_layout(tmpl_content, ""))
