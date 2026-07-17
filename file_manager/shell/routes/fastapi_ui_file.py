from __future__ import annotations
import html
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


import sass_embedded  # type: ignore[import-untyped]
import chevron  # type: ignore[import-untyped]

from file_manager.shell.sources.sqlalchemy_file import fetch_file_by_id
from file_manager.shell.sources.sqlalchemy_file import fetch_image_by_file
from file_manager.shell.sources.sqlalchemy_permissions import fetch_permissions_for
from file_manager.shell.sources.sqlalchemy_group import fetch_all_groups
from file_manager.shell.sources.sqlalchemy_dir import fetch_all_dirs
from auth.shell.sources.sqlalchemy_member import fetch_all_members


ui_files_router = APIRouter()


@ui_files_router.get("/text_file/edit/{file_id}", tags=["Auth"])
async def dashboar_text_file_edit(req: Request, file_id: str) -> HTMLResponse:
    session_owner = req.state.session.owner
    scss_loads = [Path("file_manager/shell/skins/default/"), Path("skins/default")]
    scss_file = "file_manager/shell/skins/default/detail_file/text_file.scss"
    template = "file_manager/shell/skins/default/detail_file/text_file.mustache"
    styles = ""
    
    with open(scss_file, "r",encoding="utf-8") as f:
        scss_content = f.read()
        styles = sass_embedded.compile_string(scss_content,load_paths=scss_loads).output

    data = {"styles": styles, "file_id": file_id, "editor": session_owner}

    with open(template, "r", encoding="utf-8") as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)


@ui_files_router.get("/text_file/{file_id}", tags=["Auth"])
async def dashboar_text_file(file_id: str) -> HTMLResponse:
    fl = fetch_file_by_id(file_id)

    scss_file = "file_manager/shell/skins/default/detail_file/text_file.scss"
    scss_loads = [Path("file_manager/shell/skins/default/"), Path("skins/default")]
    template = "file_manager/shell/skins/default/detail_file/text_file_read.mustache"
    styles = ""

    with open(scss_file, "r", encoding="utf-8") as f:
        scss_content = f.read()
        styles = sass_embedded.compile_string(scss_content, load_paths=scss_loads).output

    data = {
        "title": "Lorice Administratum",
        "styles": styles,
        "file_id": file_id,
        "file_name": fl.name,
        "file_content": fl.content,
        "parent_id": fl.parent_id,
    }

    with open(template, "r", encoding="utf-8",) as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)
