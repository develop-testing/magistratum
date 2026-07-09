# AGENTS.md

## Quick start

```bash
make run          # docker compose up --build (web:8800, db:8810, adminer:8820, redis:8830)
make lint         # docker compose run --rm web mypy .
make format       # docker compose run --rm web black .
make setup        # docker compose exec web python setup.py (init DB tables + seed root user)
make apply-migrations  # alembic upgrade head
```

## Architecture

- **Functional core, imperative shell**: pure domain functions in `file_manager/files.py`, `file_manager/directory.py` return `result.Result[T, str]`. Routes in `file_manager/routes/` call `.unwrap_or_raise()` to convert errors to HTTP exceptions.
- **Auth**: cookie-based (`access_token`). Sessions stored in Redis. Auth middleware at `auth/routes/auth_middleware.py` must be a `Depends` on all protected routers.
- **Routers**: mounted in `main.py` — auth & dashboard unprotected, files/dirs/groups require `Depends(auth_middleware)`.
- **Static files**: `/static` → `ui/templates/`, `/public` → `public/admin/`. Mustache templates rendered server-side, vanilla JS frontend.

## Key conventions

- Frozen dataclasses with `slots=True` for domain models
- `black` at 80 chars (`.black.toml`), `mypy --strict` (`.mypy.ini`)
- Tests use `*_test.py` pattern (pytest.ini)
- DB: MariaDB via SQLAlchemy (`database/database.py`). Redis at `fast-store:6379`.
- Alembic migrations in `database/alembic/`
