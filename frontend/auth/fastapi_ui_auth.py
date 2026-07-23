from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

import sass_embedded
import chevron  # type: ignore[import-untyped]

ui_auth_router = APIRouter()

layout = "frontend/common.mustache"


def render_auth(template_file: str, title: str) -> HTMLResponse:
    scss_file = "frontend/auth/auth.scss"

    with open(scss_file, "r", encoding="utf-8") as f:
        scss_content = f.read()

    with open(template_file, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl)

    result = sass_embedded.compile_string(
        scss_content,
        load_paths=[Path("frontend/auth/"), Path("frontend/")],
    )

    with open(layout, "r", encoding="utf-8") as f:
        html_content = chevron.render(f, {
            "title": title,
            "styles": result.output,
            "content": tmpl_content,
        })

    return HTMLResponse(html_content)


@ui_auth_router.get("/login", tags=["Auth UI"])
async def login_page() -> HTMLResponse:
    return render_auth("frontend/auth/login.mustache", "Magistratum")


@ui_auth_router.get("/register", tags=["Auth UI"])
async def register_page() -> HTMLResponse:
    return render_auth("frontend/auth/register.mustache", "Magistratum")
