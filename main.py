from __future__ import annotations

import os

# import traceback

from fastapi import HTTPException, Request, Response, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import PlainTextResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.auth.member.auth_middleware import *

from backend.auth.member.fastapi_auth import auth_router
from backend.file_manager.files.fastapi_file import files_router
from backend.file_manager.directories.fastapi_dirs import dirs_router
from backend.file_manager.groups.fastapi_groups import groups_router
from backend.auth.member.fastapi_members import member_router


from frontend.file_manager.dashboard.fastapi_ui_dashboard import ui_dashboard_router
from frontend.file_manager.detail_file.fastapi_ui_file import ui_files_router
from frontend.auth.fastapi_ui_auth import ui_auth_router
from frontend.file_manager.directory.fastapi_ui_directory import (
    ui_directory_router,
)
from frontend.members.fastapi_ui_members import ui_members_router
from frontend.not_found.fastapi_ui_not_found import render_not_found

backend = FastAPI(docs_url=None, redoc_url=None)
frontend = FastAPI()

backend.mount(
    "/public/upload", StaticFiles(directory="frontend/public/upload"), name="upload"
)
backend.mount("/public/img", StaticFiles(directory="frontend/public/img"), name="img")
backend.mount("/public", StaticFiles(directory="frontend/public/admin"), name="static")
backend.mount(
    "/static/auth",
    StaticFiles(directory="frontend/auth"),
    name="static-auth",
)
backend.mount(
    "/static/file_manager",
    StaticFiles(directory="frontend/file_manager"),
    name="static-fm",
)


@backend.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, err: HTTPException
) -> PlainTextResponse:
    return PlainTextResponse(content=str(err.detail), status_code=err.status_code)


@backend.exception_handler(ValueError)
async def value_error_handler(request: Request, err: ValueError) -> PlainTextResponse:
    return PlainTextResponse(content=str(err), status_code=400)


@backend.exception_handler(PermissionError)
async def permission_error_handler(
    request: Request, err: PermissionError
) -> PlainTextResponse:
    return PlainTextResponse(content=str(err), status_code=403)


@backend.exception_handler(RuntimeError)
async def runtime_error_handler(
    request: Request, err: RuntimeError
) -> PlainTextResponse:
    return PlainTextResponse(content=str(err), status_code=500)


@backend.exception_handler(Exception)
async def global_exception_handler(
    request: Request, err: Exception
) -> PlainTextResponse:
    return PlainTextResponse(content="Internal Server Error", status_code=500)


@backend.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=backend.openapi_url or "/openapi.json",
        title=backend.title + " - Local Swagger UI",
        swagger_js_url="/public/swagger-ui-bundle.js",
        swagger_css_url="/public/swagger-ui.css",
        swagger_favicon_url="/public/favicon.png",
    )


cors_origins = [
    o.strip()
    for o in os.environ.get("CORS_ORIGINS", "").split(",")
    if o.strip()
]

backend.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

backend.include_router(auth_router)
backend.include_router(member_router, dependencies=[Depends(auth_middleware)])
backend.include_router(dirs_router, dependencies=[Depends(auth_middleware)])
backend.include_router(groups_router, dependencies=[Depends(auth_middleware)])
backend.include_router(files_router, dependencies=[Depends(auth_middleware)])

frontend.mount(
    "/static/auth",
    StaticFiles(directory="frontend/auth"),
    name="static-auth",
)
frontend.mount(
    "/static/file_manager",
    StaticFiles(directory="frontend/file_manager"),
    name="static-fm",
)
frontend.mount(
    "/static/members",
    StaticFiles(directory="frontend/members"),
    name="static-fm",
)
frontend.mount(
    "/static/not_found",
    StaticFiles(directory="frontend/not_found"),
    name="static-nf",
)
frontend.mount(
    "/public/upload", StaticFiles(directory="frontend/public/upload"), name="upload"
)
frontend.mount("/public/img", StaticFiles(directory="frontend/public/img"), name="img")
frontend.mount("/public/default", StaticFiles(directory="default_layout"))
frontend.include_router(ui_dashboard_router, dependencies=[Depends(auth_middleware)])
frontend.include_router(ui_files_router, dependencies=[Depends(auth_middleware)])
frontend.include_router(ui_directory_router, dependencies=[Depends(auth_middleware)])
frontend.include_router(ui_members_router, dependencies=[Depends(auth_middleware)])
frontend.include_router(ui_auth_router)


@frontend.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> HTMLResponse:
    return render_not_found(request)


@frontend.exception_handler(UnauthorizedException)
async def unauthorized_handler(
    request: Request, exc: UnauthorizedException
) -> RedirectResponse:
    return RedirectResponse("/login", status_code=302)
