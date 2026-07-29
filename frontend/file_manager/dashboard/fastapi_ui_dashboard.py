from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

import chevron  # type: ignore[import-untyped]

from backend.database.database import engine
from backend.file_manager.directories.sqlalchemy_dir import fetch_dir_by_id
from mustache_default import generate_layout

ui_dashboard_router = APIRouter()


def render_dashboard(dir_id: str, username: str) -> HTMLResponse:
    template = "frontend/file_manager/dashboard/dashboard.mustache"
    parent_id: str | None = None
    if dir_id:
        conn = engine.connect()
        try:
            parent_id = fetch_dir_by_id(conn, dir_id).parent_id
        finally:
            conn.rollback()
            conn.close()

    with open(template, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(
            tmpl,
            {
                "dir_id": dir_id,
                "parent_id": parent_id,
            },
        )

    return HTMLResponse(generate_layout(tmpl_content, username))


@ui_dashboard_router.get("/dashboard/root", tags=["Auth"])
async def dashboard_root(req: Request) -> HTMLResponse:
    return render_dashboard("", req.state.session.owner)


@ui_dashboard_router.get("/dashboard/directory/{dir_id}", tags=["Auth"])
async def dashboard_directory(req: Request, dir_id: str) -> HTMLResponse:
    return render_dashboard(dir_id, req.state.session.owner)
