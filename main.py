from __future__ import annotations

# import traceback

from fastapi import HTTPException, Request, Response, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from auth.shell.routes.auth_middleware import *

from auth.shell.routes.fastapi_auth import auth_router
from file_manager.shell.routes.fastapi_file import files_router
from file_manager.shell.routes.fastapi_dirs import dirs_router
from file_manager.shell.routes.fastapi_dir_node import dir_node_router
from file_manager.shell.routes.fastapi_groups import groups_router
from file_manager.shell.routes.fastapi_dashboard import ui_dashboard_router
from file_manager.shell.routes.fastapi_files_routes import ui_files_router
from auth.shell.routes.fastapi_auth_ui import ui_auth_router

backend = FastAPI(docs_url=None, redoc_url=None)
frontend = FastAPI()

backend.mount("/public", StaticFiles(directory="public/admin"), name="static")
backend.mount("/public/images", StaticFiles(directory="public/images"), name="images")
backend.mount("/static/auth", StaticFiles(directory="auth/shell/skins/default/auth"), name="static-auth")
backend.mount("/static/file_manager", StaticFiles(directory="file_manager/shell/skins/default"), name="static-fm")


@backend.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, err: HTTPException
) -> PlainTextResponse:
    return PlainTextResponse(content=str(err.detail), status_code=err.status_code)


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


backend.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8800",
        "http://localhost:8800",
        "http://127.0.0.1:8840",
        "http://localhost:8840",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

backend.include_router(auth_router)
backend.include_router(dirs_router, dependencies=[Depends(auth_middleware)])
backend.include_router(dir_node_router, dependencies=[Depends(auth_middleware)])
backend.include_router(groups_router, dependencies=[Depends(auth_middleware)])
backend.include_router(files_router, dependencies=[Depends(auth_middleware)])

frontend.mount("/static/auth", StaticFiles(directory="auth/shell/skins/default/auth"), name="static-auth")
frontend.mount("/static/file_manager", StaticFiles(directory="file_manager/shell/skins/default"), name="static-fm")
frontend.mount("/public/images", StaticFiles(directory="public/images"), name="images")

frontend.include_router(ui_dashboard_router, dependencies=[Depends(auth_middleware)])
frontend.include_router(ui_files_router, dependencies=[Depends(auth_middleware)])
frontend.include_router(ui_auth_router)
