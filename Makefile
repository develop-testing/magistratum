run:
	docker compose up --build

stop:
	docker compose stop

logs:
	docker compose logs -f

lint:
	docker compose run --rm backend mypy .

format:
	docker compose run --rm backend black .

test:
	docker compose run --rm backend pytest .

functional-test:
	docker compose run --rm backend pytest backend/tests -m functional

web-command:
	docker compose exec backend $(cmd)

dump-req:
	docker compose exec backend pip freeze > requirements.txt

install-req:
	docker compose exec backend pip install -r requirements.txt

setup:
	docker compose exec backend python setup.py

init-alembic:
	docker compose exec backend alembic init backend/database/alembic

create-migrations:
	docker compose exec backend alembic revision --autogenerate -m "init"

apply-migrations:
	docker compose exec backend alembic upgrade head
