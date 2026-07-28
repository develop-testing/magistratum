from __future__ import annotations

from fastapi import Request
from fastapi.responses import HTMLResponse

import chevron  # type: ignore[import-untyped]

from mustache_default import generate_layout


def render_not_found(request: Request) -> HTMLResponse:
    template = "frontend/not_found/not_found.mustache"

    with open(template, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl)

    username = ""
    if hasattr(request.state, "session"):
        username = request.state.session.owner

    return HTMLResponse(generate_layout(tmpl_content, username), status_code=404)
