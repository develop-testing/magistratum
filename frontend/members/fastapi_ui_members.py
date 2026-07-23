from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

import chevron  # type: ignore[import-untyped]

ui_members_router = APIRouter()


@ui_members_router.get("/members", tags=["Members"])
async def members_page() -> HTMLResponse:
    template = "frontend/members/members.mustache"
    layout = "frontend/common.mustache"

    with open(template, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl)

    with open(layout, "r", encoding="utf-8") as f:
        html_content = chevron.render(f, {
            "title": "Members",
            "content": tmpl_content,
        })

    return HTMLResponse(html_content)
