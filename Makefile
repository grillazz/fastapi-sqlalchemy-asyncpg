.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build:	## Build project with compose
	docker-compose build

.PHONY: up
up:	## Run project with compose
	docker-compose up --remove-orphans

.PHONY: clean
clean: ## Clean Reset project containers and volumes with compose
	docker-compose down -v --remove-orphans | true
	docker-compose rm -f | true
	docker volume rm fastapi_postgres_data | true

.PHONY: migrate-apply
migrate-apply: ## apply alembic migrations to database/schema
	docker-compose run --rm app alembic upgrade head

.PHONY: migrate-create
migrate-create: ## create new alembic migration
	docker-compose run --rm app alembic revision --autogenerate

.PHONY: requirements
requirements:	## Refresh requirements.txt from pipfile.lock
	pipenv lock --requirements --dev >| requirements.txt

.PHONY: test
test:	## Run project tests
	docker-compose -f docker-compose.yml -f docker-compose.test.yml  run --rm app pytest

.PHONY: safety
safety:	## Check project and dependencies with safety https://github.com/pyupio/safety
	docker-compose run --rm app safety check

.PHONY: py-upgrade
py-upgrade:	## Upgrade project py files with pyupgrade library for python version 3.10
	pyupgrade --py310-plus `find app -name "*.py"`

.PHONY: lint
lint:  ## Lint project code.
	poetry run ruff .

.PHONY: format
format:  ## Format project code.
	isort app tests
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app tests --exclude=__init__.py
	black app tests --line-length=120

.PHONY: slim-build
slim-build: ## with power of docker-slim build smaller and safer images
	docker-slim build --compose-file docker-compose.yml --target-compose-svc app --dep-include-target-compose-svc-deps true --http-probe-exec app fastapi-sqlalchemy-asyncpg_app:latest

.PHONY: feed_db
feed_db: ## create database objects and insert data
	docker-compose exec db psql devdb user -f /home/gx/code/shakespeare_work.sql | true
	docker-compose exec db psql devdb user -f /home/gx/code/shakespeare_chapter.sql | true
	docker-compose exec db psql devdb user -f /home/gx/code/shakespeare_wordform.sql | true
	docker-compose exec db psql devdb user -f /home/gx/code/shakespeare_character.sql | true
	docker-compose exec db psql devdb user -f /home/gx/code/shakespeare_paragraph.sql | true
	docker-compose exec db psql devdb user -f /home/gx/code/shakespeare_character_work.sql