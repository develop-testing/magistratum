from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

import chevron  # type: ignore[import-untyped]

from backend.file_manager.directory_node.sqlalchemy_home_dir import (
    fetch_home_dir_by_username,
)
from backend.file_manager.directories.sqlalchemy_dir import fetch_dir_by_id
from mustache_default import generate_layout

ui_dashboard_router = APIRouter()


def render_dashboard(dir_id: str, username: str) -> HTMLResponse:
    dr = fetch_dir_by_id(dir_id)

    template = "frontend/file_manager/dashboard/dashboard.mustache"

    with open(template, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(
            tmpl,
            {
                "dir_id": dir_id,
                "parent_id": dr.parent_id,
            },
        )

    return HTMLResponse(generate_layout(tmpl_content, username))


@ui_dashboard_router.get("/dashboard/home", tags=["Auth"])
async def dashboar_home(req: Request) -> HTMLResponse:
    session_owner = req.state.session.owner
    home = fetch_home_dir_by_username(session_owner)

    return render_dashboard(home.dir_id, session_owner)


@ui_dashboard_router.get("/dashboard/directory/{dir_id}", tags=["Auth"])
async def dashboard_directory(req: Request, dir_id: str) -> HTMLResponse:
    return render_dashboard(dir_id, req.state.session.owner)
