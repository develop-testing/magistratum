from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

import chevron  # type: ignore[import-untyped]

ui_auth_router = APIRouter()

layout = "frontend/common.mustache"


def render_auth(template_file: str, title: str) -> HTMLResponse:
    with open(template_file, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl)

    with open(layout, "r", encoding="utf-8") as f:
        html_content = chevron.render(
            f,
            {
                "title": title,
                "content": tmpl_content,
            },
        )

    return HTMLResponse(html_content)


@ui_auth_router.get("/login", tags=["Auth UI"])
async def login_page() -> HTMLResponse:
    return render_auth("frontend/auth/login.mustache", "Magistratum")
