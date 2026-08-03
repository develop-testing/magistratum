from __future__ import annotations

import chevron  # type: ignore[import-untyped]

layout = "frontend/default_layout/default.mustache"


def generate_layout(content: str, username: str) -> str:
    with open(layout, "r", encoding="utf-8") as f:
        html_content: str = chevron.render(
            f,
            {
                "title": "Magistratum",
                "content": content,
                "is_root": username == "root",
            },
        )

    return html_content
