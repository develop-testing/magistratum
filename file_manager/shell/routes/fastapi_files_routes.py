from __future__ import annotations
import html
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

import sass_embedded
import chevron  # type: ignore[import-untyped]

from file_manager.shell.sources.sqlalchemy_file import fetch_file_by_id
from file_manager.shell.sources.sqlalchemy_file import fetch_image_by_file
from file_manager.shell.sources.sqlalchemy_permissions import fetch_permissions_for
from file_manager.shell.sources.sqlalchemy_group import fetch_all_groups
from file_manager.shell.sources.sqlalchemy_dir import fetch_all_dirs
from auth.shell.sources.sqlalchemy_member import fetch_all_members


def _perm_code_to_value(code: str) -> str:
    if code == "r-":
        return "r"
    if code == "-w":
        return "w"
    if code == "rw":
        return "rw"
    return ""


ui_files_router = APIRouter()


@ui_files_router.get("/text_file/edit/{file_id}", tags=["Auth"])
async def dashboar_text_file_edit(file_id: str) -> HTMLResponse:
    fl = fetch_file_by_id(file_id)

    with open(
        "file_manager/shell/skins/default/detail_file/text_file.scss",
        "r",
        encoding="utf-8",
    ) as f:
        scss_content = f.read()

    result = sass_embedded.compile_string(
        scss_content,
        load_paths=[Path("file_manager/shell/skins/default/"), Path("skins/default")],
    )

    prms = fetch_permissions_for([fl.file_id])
    prm = next((p for p in prms if p.item_id == fl.file_id), None)

    group_perm_value = _perm_code_to_value(prm.content[0:2]) if prm else ""
    other_perm_value = _perm_code_to_value(prm.content[2:4]) if prm else ""
    perm_owner = prm.owner_name if prm else ""

    image_url = fetch_image_by_file(file_id)

    data = {
        "title": "Lorice Administratum",
        "styles": result.output,
        "file_id": file_id,
        "file_name": fl.name,
        "file_content": html.unescape(fl.content),
        "parent_id": fl.parent_id,
        "perm_owner": perm_owner,
        "is_group_r": group_perm_value == "r",
        "is_group_w": group_perm_value == "w",
        "is_group_rw": group_perm_value == "rw",
        "is_other_r": other_perm_value == "r",
        "is_other_w": other_perm_value == "w",
        "is_other_rw": other_perm_value == "rw",
        "image_url": image_url,
        "all_users": [
            {"name": m.username, "is_current": m.username == perm_owner}
            for m in fetch_all_members()
        ],
        "all_groups": [
            {"name": g, "is_current": g == (prm.group_name if prm else "")}
            for g in fetch_all_groups()
        ],
        "all_dirs": [
            {"dir_id": d.dir_id, "name": d.name, "is_current": d.dir_id == fl.parent_id}
            for d in fetch_all_dirs()
        ],
    }

    with open(
        "file_manager/shell/skins/default/detail_file/text_file.mustache",
        "r",
        encoding="utf-8",
    ) as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)


@ui_files_router.get("/text_file/{file_id}", tags=["Auth"])
async def dashboar_text_file(file_id: str) -> HTMLResponse:
    fl = fetch_file_by_id(file_id)

    with open(
        "file_manager/shell/skins/default/detail_file/text_file.scss",
        "r",
        encoding="utf-8",
    ) as f:
        scss_content = f.read()

    result = sass_embedded.compile_string(
        scss_content,
        load_paths=[Path("file_manager/shell/skins/default/"), Path("skins/default")],
    )

    data = {
        "title": "Lorice Administratum",
        "styles": result.output,
        "file_id": file_id,
        "file_name": fl.name,
        "file_content": fl.content,
        "parent_id": fl.parent_id,
    }

    with open(
        "file_manager/shell/skins/default/detail_file/text_file_read.mustache",
        "r",
        encoding="utf-8",
    ) as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)
