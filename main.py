from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from routes.auth import auth_router

app = FastAPI(docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8800", "http://localhost:8800"],
    allow_credentials=True,          
    allow_methods=["*"],             
    allow_headers=["*"],             
)

@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url, # FastAPI сам отдаст схему в Scalar
        title="Мой Проект API — Scalar",
        servers=[{"url": "http://127.0.0.1:8800"}],
    )

app.include_router(auth_router)
