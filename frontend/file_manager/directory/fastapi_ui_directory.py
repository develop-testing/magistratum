from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

import sass_embedded
import chevron  # type: ignore[import-untyped]

ui_directory_router = APIRouter()

layout = "frontend/common.mustache"


@ui_directory_router.get("/dir/edit/{dir_id}", tags=["Auth"])
async def dashboar(dir_id: str) -> HTMLResponse:
    scss_file = "frontend/file_manager/directory/dir_edit.scss"
    template_file = "frontend/file_manager/directory/dir_edit.mustache"

    with open(scss_file, "r", encoding="utf-8") as f:
        scss_content = f.read()

    result = sass_embedded.compile_string(
        scss_content,
        load_paths=[
            Path("frontend/file_manager/directory/"),
            Path("frontend/"),
        ],
    )

    with open(template_file, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl)

    with open(layout, "r", encoding="utf-8") as f:
        html_content = chevron.render(f, {
            "title": "Lorice Administratum",
            "styles": result.output,
            "content": tmpl_content,
        })

    return HTMLResponse(html_content)
