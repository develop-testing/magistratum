# AGENTS.md

## Quick start

```bash
make run          # docker compose up --build (backend:8800, frontend:8840, db:8810, adminer:8820, redis:8830)
make lint         # docker compose run --rm backend mypy .
make format       # docker compose run --rm backend black .
make setup        # docker compose exec backend python setup.py (init DB tables + seed root user)
make apply-migrations  # alembic upgrade head
```

## Architecture

- **Functional core, imperative shell**: pure domain functions in `backend/file_manager/files.py`, `backend/file_manager/directories/` return `result.Result[T, str]`. Routes in `backend/file_manager/shell/routes/` call `.unwrap_or_raise()` to convert errors to HTTP exceptions.
- **Auth**: cookie-based (`access_token`). Sessions stored in Redis. Auth middleware at `backend/auth/shell/routes/auth_middleware.py` must be a `Depends` on all protected routers.
- **Backend routers**: mounted in `main.py` — auth & dashboard unprotected, files/dirs/groups require `Depends(auth_middleware)`.
- **Frontend routers**: UI routes in `frontend/auth/`, `frontend/file_manager/{dashboard,detail_file,directory}/` render server-side Mustache templates.
- **Static files**: `/static/auth` → `frontend/auth/`, `/static/file_manager` → `frontend/file_manager/`, `/public` → `frontend/public/admin/`. Mustache templates rendered server-side, vanilla JS frontend.

## Directory structure

```
app/
├── main.py              # FastAPI app definitions (backend + frontend)
├── setup.py             # DB init + seed script
├── backend/             # API layer
│   ├── auth/            # Auth domain (member, session) + routes + sources
│   ├── database/        # DB engine, Redis, Alembic
│   │   └── alembic/     # Migrations
│   ├── file_manager/    # File/dir/group domain + routes + sources
│   └── router/          # Shared HTTP exception classes
├── frontend/            # UI layer
│   ├── auth/            # Login/register UI (templates, SCSS, JS)
│   ├── file_manager/    # File manager UI
│   │   ├── dashboard/   # Dashboard page
│   │   ├── detail_file/ # File editor/viewer (incl. TinyMCE)
│   │   └── directory/   # Directory edit page
│   ├── public/          # Static assets (swagger, uploads, images)
│   └── skins/default/   # Common SCSS/JS
└── configs...
```

## Key conventions

- Frozen dataclasses with `slots=True` for domain models
- `black` at 80 chars (`.black.toml`), `mypy --strict` (`.mypy.ini`)
- Tests use `*_test.py` pattern (pytest.ini)
- DB: MariaDB via SQLAlchemy (`backend/database/database.py`). Redis at `fast-store:6379`.
- Alembic migrations in `backend/database/alembic/`
- Python imports use `backend.` and `frontend.` prefixes (namespace packages, no `__init__.py`)
