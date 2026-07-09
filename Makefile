run:
	docker compose up --build

stop:
	docker compose stop

logs:
	docker compose logs -f

lint:
	docker compose run --rm web mypy .

format:
	docker compose run --rm web black .

web-command:
	docker compose exec web $(cmd)

dump-req:
	docker compose exec web pip freeze > requirements.txt

install-req:
	docker compose exec web pip install -r requirements.txt

setup:
	docker compose exec web python setup.py

init-alembic:
	docker compose exec web alembic init database/alembic

create-migrations:
	docker compose exec web alembic revision --autogenerate -m "init"

apply-migrations:
	docker compose exec web alembic upgrade head