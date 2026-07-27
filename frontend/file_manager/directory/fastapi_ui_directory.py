from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

import chevron  # type: ignore[import-untyped]

from mustache_default import generate_layout

ui_directory_router = APIRouter()


@ui_directory_router.get("/dir/edit/{dir_id}", tags=["Auth"])
async def dashboar(req: Request, dir_id: str) -> HTMLResponse:
    template_file = "frontend/file_manager/directory/dir_edit.mustache"

    with open(template_file, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl)

    return HTMLResponse(
        generate_layout(tmpl_content, req.state.session.owner)
    )
