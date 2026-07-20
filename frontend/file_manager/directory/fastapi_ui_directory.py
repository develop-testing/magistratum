from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

import sass_embedded
import chevron  # type: ignore[import-untyped]

ui_directory_router = APIRouter()

@ui_directory_router.get("/dir/edit/{dir_id}", tags=["Auth"])
async def dashboar(dir_id: str) -> HTMLResponse:
    scss_file = "frontend/file_manager/directory/dir_edit.scss"
    template_file = "frontend/file_manager/directory/dir_edit.mustache"
    html_conten = ""

    with open(scss_file, "r", encoding="utf-8") as f:
        scss_content = f.read()

        result = sass_embedded.compile_string(
            scss_content,
            load_paths=[Path("frontend/file_manager/directory/"), Path("frontend/skins/default/")],
        )

    data = {
        "title": "Lorice Administratum",
        "styles": result.output
    }

    with open(template_file, "r", encoding="utf-8") as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)