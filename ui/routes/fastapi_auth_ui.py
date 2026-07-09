from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

import sass_embedded
import chevron  # type: ignore[import-untyped]

ui_auth_router = APIRouter()


@ui_auth_router.get("/login", tags=["Auth UI"])
async def login_page() -> HTMLResponse:
    return render_auth_page("Lorice Administratum — Вход", "login")


@ui_auth_router.get("/register", tags=["Auth UI"])
async def register_page() -> HTMLResponse:
    return render_auth_page("Lorice Administratum — Регистрация", "register")


def render_auth_page(title: str, template_name: str) -> HTMLResponse:
    with open("ui/templates/auth/auth.scss", "r", encoding="utf-8") as f:
        scss_content = f.read()

    result = sass_embedded.compile_string(
        scss_content, load_paths=[Path("ui/templates/")]
    )

    data = {"title": title, "styles": result.output}

    with open(
        f"ui/templates/auth/{template_name}.mustache", "r", encoding="utf-8"
    ) as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)
