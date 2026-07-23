from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

import sass_embedded
import chevron  # type: ignore[import-untyped]

from backend.file_manager.shell.sources.sqlalchemy_home_dir import fetch_home_dir_by_username
from backend.file_manager.shell.sources.sqlalchemy_dir import fetch_dir_by_id

ui_dashboard_router = APIRouter()

layout = "frontend/common.mustache"


def render_dashboard(dir_id: str) -> HTMLResponse:
    dr = fetch_dir_by_id(dir_id)

    scss_file = "frontend/file_manager/dashboard/dashboard.scss"
    template = "frontend/file_manager/dashboard/dashboard.mustache"

    with open(scss_file, "r", encoding="utf-8") as f:
        scss_content = f.read()

    with open(template, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl, {
            "dir_id": dir_id,
            "parent_id": dr.parent_id,
        })

    result = sass_embedded.compile_string(
        scss_content,
        load_paths=[Path("frontend/file_manager/dashboard/"), Path("frontend/")],
    )

    with open(layout, "r", encoding="utf-8") as f:
        html_content = chevron.render(f, {
            "title": "Lorice Administratum",
            "styles": result.output,
            "content": tmpl_content,
        })

    return HTMLResponse(html_content)


@ui_dashboard_router.get("/dashboard/home", tags=["Auth"])
async def dashboar_home(req: Request) -> HTMLResponse:
    session_owner = req.state.session.owner
    home = fetch_home_dir_by_username(session_owner)

    return render_dashboard(home.dir_id)


@ui_dashboard_router.get("/dashboard/directory/{dir_id}", tags=["Auth"])
async def dashboard_directory(dir_id: str) -> HTMLResponse:
    return render_dashboard(dir_id)
