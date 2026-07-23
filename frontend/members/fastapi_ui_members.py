from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

import sass_embedded
import chevron  # type: ignore[import-untyped]

ui_members_router = APIRouter()


@ui_members_router.get("/members", tags=["Members"])
async def members_page() -> HTMLResponse:
    scss_file = "frontend/members/members.scss"
    template = "frontend/members/members.mustache"
    layout = "frontend/common.mustache"

    with open(scss_file, "r", encoding="utf-8") as f:
        scss_content = f.read()

    with open(template, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl)

    result = sass_embedded.compile_string(
        scss_content,
        load_paths=[
            Path("frontend/members/"),
            Path("frontend/"),
        ],
    )

    with open(layout, "r", encoding="utf-8") as f:
        html_content = chevron.render(f, {
            "title": "Members",
            "styles": result.output,
            "content":tmpl_content,
        })

    return HTMLResponse(html_content)
