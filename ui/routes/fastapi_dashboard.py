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


@ui_dashboard_router.get("/dashboar", tags=["Auth"])
async def login() -> HTMLResponse:

    with open("ui/templates/assets/dashboard.scss", "r", encoding="utf-8") as f:
        scss_content = f.read()

    result = sass_embedded.compile_string(
        scss_content, load_paths=[Path("ui/templates/assets/")]
    )

    data = {
        "title": "Lorice Administratum",
        "styles": result.output,
    }

    with open("ui/templates/dashboard.mustache", "r", encoding="utf-8") as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)
