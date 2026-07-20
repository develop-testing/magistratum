from __future__ import annotations
import html
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


import sass_embedded
import chevron  # type: ignore[import-untyped]

from backend.file_manager.shell.sources.sqlalchemy_file import fetch_file_by_id
from backend.file_manager.shell.sources.sqlalchemy_file import fetch_image_by_file
from backend.file_manager.shell.sources.sqlalchemy_permissions import fetch_permissions_for
from backend.file_manager.shell.sources.sqlalchemy_group import fetch_all_groups
from backend.file_manager.shell.sources.sqlalchemy_dir import fetch_all_dirs
from backend.auth.shell.sources.sqlalchemy_member import fetch_all_members

ui_files_router = APIRouter()


@ui_files_router.get("/text_file/edit/{file_id}", tags=["Auth"])
async def dashboar_text_file_edit(req: Request, file_id: str) -> HTMLResponse:
    session_owner = req.state.session.owner
    scss_loads = [Path("frontend/file_manager/detail_file/"), Path("frontend/skins/default/")]
    scss_file = "frontend/file_manager/detail_file/text_file.scss"
    template = "frontend/file_manager/detail_file/text_file.mustache"
    styles: str | None = ""

    with open(scss_file, "r", encoding="utf-8") as f:
        scss_content = f.read()
        styles = sass_embedded.compile_string(
            scss_content, load_paths=scss_loads
        ).output

    data = {"styles": styles, "editor": session_owner}

    with open(template, "r", encoding="utf-8") as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)


@ui_files_router.get("/text_file/{file_id}", tags=["Auth"])
async def dashboar_text_file(file_id: str) -> HTMLResponse:
    scss_file = "frontend/file_manager/detail_file/text_file.scss"
    scss_loads = [Path("frontend/file_manager/detail_file/"), Path("frontend/skins/default/")]
    template = "frontend/file_manager/detail_file/text_file_read.mustache"
    styles: str | None = ""

    with open(scss_file, "r", encoding="utf-8") as f:
        scss_content = f.read()
        styles = sass_embedded.compile_string(
            scss_content, load_paths=scss_loads
        ).output

    data = {"title": "Lorice Administratum", "styles": styles}

    with open(template, "r", encoding="utf-8",) as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)
