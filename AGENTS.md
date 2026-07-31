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
│   ├── common.js          # Shared JS (send_get, send_post, send_delete, send_patch)
│   └── common.scss        # Shared SCSS
└── configs...
```

## Key conventions

- Frozen dataclasses with `slots=True` for domain models
- `black` at 80 chars (`.black.toml`), `mypy --strict` (`.mypy.ini`)
- Tests live in `test_<module>.py` files next to their modules, plain `assert` + `pytest.raises` (pytest, `make test`)
- Functional (API lifecycle) tests in `backend/tests/` against the running stack, marked `functional`, run via `make functional-test` (requires `make run` + `make setup` for root/root user). Shared HTTP helpers in `backend/tests/api_client.py`.
- DB: MariaDB via SQLAlchemy (`backend/database/database.py`). Redis at `fast-store:6379`.
- Alembic migrations in `backend/database/alembic/`
- Python imports use `backend.` and `frontend.` prefixes (namespace packages, no `__init__.py`)

Общие правила.

- Код функциональный, все структуры неизменяемые, значит изменяеющие функции возвращают копию.
- Для ошибок используются исключения. Работа с result затруднинельна в связи с отсутствием быстрого выхода.
- Проект строится по принципам модульного монолита. Модуль состоит из директории(module) основного файла(module.py) и файлов для работы с внешней средой (базы данны, апиб файловвая система) которые имеют префикс соответсвующей технологии.

Создание структур.

- Конструкторы как отдельные функции. Префиксы конструкторов new\_ - любое создание структуры с генерацией данных, mk\_ - создание со всеми аргументами.
- Каждый new конструктор и изменяющая функция создает новый экземпляр структуры.
- Придерживаемся принципа трех: три поля, три вложенности, три функции для структуры и другое, три шага. Подход должен уменьшить когнитивную нагрузку.

Функции.

- Все функции, независимо процедлура или рассчет, должны возвращать значение для продолжения пайплайна.
- Функции работы с внешней средой именуются префиксами: fetch, save, delete и другие.
