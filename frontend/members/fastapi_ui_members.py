from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

import chevron  # type: ignore[import-untyped]

from mustache_default import generate_layout

ui_members_router = APIRouter()


@ui_members_router.get("/members", tags=["Members"])
async def members_page(req: Request) -> HTMLResponse:
    template = "frontend/members/members.mustache"

    with open(template, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl)

    return HTMLResponse(generate_layout(tmpl_content, req.state.session.owner))
