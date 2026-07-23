from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

import chevron  # type: ignore[import-untyped]

ui_directory_router = APIRouter()

layout = "frontend/common.mustache"


@ui_directory_router.get("/dir/edit/{dir_id}", tags=["Auth"])
async def dashboar(dir_id: str) -> HTMLResponse:
    template_file = "frontend/file_manager/directory/dir_edit.mustache"

    with open(template_file, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl)

    with open(layout, "r", encoding="utf-8") as f:
        html_content = chevron.render(
            f,
            {
                "title": "Magistratum",
                "content": tmpl_content,
            },
        )

    return HTMLResponse(html_content)
