from __future__ import annotations

from fastapi import FastAPI

from routes.auth import auth_router

app = FastAPI()
app.include_router(auth_router)
