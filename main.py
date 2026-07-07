from __future__ import annotations

# import traceback

from fastapi import HTTPException, Request, Response, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from auth.routes.auth_middleware import *

from auth.routes.fastapi_auth import auth_router
from file_manager.routes.fastapi_file import files_router
from file_manager.routes.fastapi_dirs import dirs_router
from file_manager.routes.fastapi_groups import groups_router
from ui.routes.fastapi_dashboard import ui_dashboard_router

app = FastAPI(docs_url=None, redoc_url=None)

app.mount("/public", StaticFiles(directory="public/admin"), name="static")
app.mount("/static", StaticFiles(directory="ui/templates/assets"), name="static")


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, err: HTTPException
) -> PlainTextResponse:
    return PlainTextResponse(content=str(err.detail), status_code=err.status_code)


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request, err: Exception
) -> PlainTextResponse:
    return PlainTextResponse(content="Internal Server Error", status_code=500)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=app.openapi_url or "/openapi.json",
        title=app.title + " - Local Swagger UI",
        swagger_js_url="/public/swagger-ui-bundle.js",
        swagger_css_url="/public/swagger-ui.css",
        swagger_favicon_url="/public/favicon.png",
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8800", "http://localhost:8800"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(ui_dashboard_router)
app.include_router(dirs_router, dependencies=[Depends(auth_middleware)])
app.include_router(groups_router, dependencies=[Depends(auth_middleware)])
app.include_router(files_router, dependencies=[Depends(auth_middleware)])
