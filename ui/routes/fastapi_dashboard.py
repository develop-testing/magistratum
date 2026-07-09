from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

import sass_embedded
import chevron  # type: ignore[import-untyped]

from router.response import BadRequest
from file_manager.sources.sqlalchemy_home_dir import fetch_home_dir_by_username

ui_dashboard_router = APIRouter()


@ui_dashboard_router.get("/dashboar/directory/{dir_id}", tags=["Auth"])
async def dashboar(dir_id: str) -> HTMLResponse:
    return render_dashboard(dir_id)


@ui_dashboard_router.get("/dashboar/home", tags=["Auth"])
async def dashboar_home(req: Request) -> HTMLResponse:
    session_owner = req.state.session.owner
    home = fetch_home_dir_by_username(session_owner).unwrap_or_raise(BadRequest)

    return render_dashboard(home.dir_id)


def render_dashboard(dir_id: str) -> HTMLResponse:
    with open("ui/templates/dashboard/dashboard.scss", "r", encoding="utf-8") as f:
        scss_content = f.read()

    result = sass_embedded.compile_string(
        scss_content, load_paths=[Path("ui/templates/")]
    )

    data = {"title": "Lorice Administratum", "styles": result.output, "dir_id": dir_id}

    with open("ui/templates/dashboard/dashboard.mustache", "r", encoding="utf-8") as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)
