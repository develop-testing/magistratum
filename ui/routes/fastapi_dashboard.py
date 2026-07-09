from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import sass_embedded


import chevron  # type: ignore[import-untyped]

ui_dashboard_router = APIRouter()


data = {"title": "Lorica Administratum"}


@ui_dashboard_router.get("/dashboar/{dir_id}", tags=["Auth"])
async def dashboar(dir_id: str) -> HTMLResponse:

    with open("ui/templates/dashboard/dashboard.scss", "r", encoding="utf-8") as f:
        scss_content = f.read()

    result = sass_embedded.compile_string(
        scss_content, load_paths=[Path("ui/templates/")]
    )

    data = {"title": "Lorice Administratum", "styles": result.output, "dir_id": dir_id}

    with open("ui/templates/dashboard/dashboard.mustache", "r", encoding="utf-8") as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)
