from __future__ import annotations


from fastapi import Response, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, HTMLResponse
from scalar_fastapi import get_scalar_api_reference  # type: ignore[import-not-found]

from routes.auth_middleware import *

from routes.auth import auth_router
from routes.files import files_router

app = FastAPI(docs_url=None, redoc_url=None)


@app.get("/docs", include_in_schema=False)
async def scalar_html() -> HTMLResponse:
    scalar_content = get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar for lorica",
        servers=[{"url": "http://127.0.0.1:8800"}],
    )

    return HTMLResponse(content=scalar_content)


@app.exception_handler(UnauthorizedException)
async def unauthorized_plain_handler(
    request: Response, exc: UnauthorizedException
) -> PlainTextResponse:
    return PlainTextResponse(content=str(exc.detail), status_code=exc.status_code)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8800", "http://localhost:8800"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(files_router, dependencies=[Depends(auth_middleware)])
