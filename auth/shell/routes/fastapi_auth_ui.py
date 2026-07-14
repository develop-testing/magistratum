from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

import sass_embedded
import chevron  # type: ignore[import-untyped]

ui_auth_router = APIRouter()


@ui_auth_router.get("/login", tags=["Auth UI"])
async def login_page() -> HTMLResponse:
    with open("auth/shell/skins/default/auth/auth.scss", "r", encoding="utf-8") as f:
        scss_content = f.read()

    result = sass_embedded.compile_string(
        scss_content,
        load_paths=[Path("auth/shell/skins/default/"), Path("skins/default")],
    )

    data = {"title": "Magistratum", "styles": result.output}

    with open(
        "auth/shell/skins/default/auth/login.mustache", "r", encoding="utf-8"
    ) as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)
