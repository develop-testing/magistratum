from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

import chevron  # type: ignore[import-untyped]

from mustache_default import generate_layout

ui_auth_router = APIRouter()


def render_auth(template_file: str) -> HTMLResponse:
    with open(template_file, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl)

    return HTMLResponse(generate_layout(tmpl_content, ""))


@ui_auth_router.get("/login", tags=["Auth UI"])
async def login_page() -> HTMLResponse:
    return render_auth("frontend/auth/login.mustache")
