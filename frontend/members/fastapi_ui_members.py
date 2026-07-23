from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

import sass_embedded
import chevron  # type: ignore[import-untyped]

ui_members_router = APIRouter()


@ui_members_router.get("/members", tags=["Members"])
async def members_page() -> HTMLResponse:
    with open(
        "frontend/members/members.scss",
        "r",
        encoding="utf-8",
    ) as f:
        scss_content = f.read()

    result = sass_embedded.compile_string(
        scss_content,
        load_paths=[
            Path("frontend/members/"),
            Path("frontend/skins/default/"),
        ],
    )

    data = {
        "title": "Members",
        "styles": result.output,
    }

    with open(
        "frontend/members/members.mustache",
        "r",
        encoding="utf-8",
    ) as f:
        html_content = chevron.render(f, data)

    return HTMLResponse(html_content)
