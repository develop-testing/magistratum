from __future__ import annotations


from fastapi import Response, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from routes.auth_middleware import *

from routes.auth import auth_router
from routes.files import files_router

app = FastAPI(docs_url=None, redoc_url=None)

app.mount("/public", StaticFiles(directory="public/admin"), name="static")

@app.exception_handler(UnauthorizedException)
async def unauthorized_plain_handler(
    request: Response, exc: UnauthorizedException
) -> PlainTextResponse:
    return PlainTextResponse(content=str(exc.detail), status_code=exc.status_code)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=app.openapi_url or "/openapi.json",
        title=app.title + " - Local Swagger UI",
        swagger_js_url="/public/swagger-ui-bundle.js",
        swagger_css_url="/public/swagger-ui.css",
        swagger_favicon_url="/public/favicon.png",
    )  # type: ignore[no-any-return]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8800", "http://localhost:8800"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(files_router, dependencies=[Depends(auth_middleware)])
