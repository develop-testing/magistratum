from __future__ import annotations
from fastapi.responses import HTMLResponse

import chevron  # type: ignore[import-untyped]

layout = "frontend/common.mustache"


def render_not_found() -> HTMLResponse:
    template = "frontend/not_found/not_found.mustache"

    with open(template, "r", encoding="utf-8") as tmpl:
        tmpl_content = chevron.render(tmpl)

    with open(layout, "r", encoding="utf-8") as f:
        html_content = chevron.render(
            f,
            {
                "title": "404",
                "content": tmpl_content,
            },
        )

    return HTMLResponse(html_content, status_code=404)
