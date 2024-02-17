.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: docker-build
docker-build:	## Build project with compose
	docker-compose build

.PHONY: docker-up
docker-up:	## Run project with compose
	docker-compose up --remove-orphans

.PHONY: docker-clean
docker-clean: ## Clean Reset project containers and volumes with compose
	docker-compose down -v --remove-orphans | true
	docker-compose rm -f | true
	docker volume rm fastapi_postgres_data | true

.PHONY: docker-apply-db-migrations
docker-apply-db-migrations: ## apply alembic migrations to database/schema
	docker-compose run --rm app alembic upgrade head

.PHONY: docker-create-db-migration
docker-create-db-migration:  ## Create new alembic database migration aka database revision.
	docker-compose up -d db | true
	docker-compose run --no-deps app alembic revision --autogenerate -m "$(msg)"

.PHONY: docker-test
docker-test:	## Run project tests
	docker-compose -f docker-compose.yml -f docker-compose.test.yml  run --rm app pytest

.PHONY: safety
safety:	## Check project and dependencies with safety https://github.com/pyupio/safety
	docker-compose run --rm app safety check

.PHONY: py-upgrade
py-upgrade:	## Upgrade project py files with pyupgrade library for python version 3.10
	pyupgrade --py312-plus `find app -name "*.py"`

.PHONY: lint
lint:  ## Lint project code.
	poetry run ruff --fix .

.PHONY: slim-build
slim-build: ## with power of docker-slim build smaller and safer images
	docker-slim build --compose-file docker-compose.yml --target-compose-svc app --dep-include-target-compose-svc-deps true --http-probe-exec app fastapi-sqlalchemy-asyncpg_app:latest

.PHONY: docker-feed-database
docker-feed-database: ## create database objects and insert data
	docker-compose exec db psql devdb user -f /home/gx/code/shakespeare_work.sql | true
	docker-compose exec db psql devdb user -f /home/gx/code/shakespeare_chapter.sql | true
	docker-compose exec db psql devdb user -f /home/gx/code/shakespeare_wordform.sql | true
	docker-compose exec db psql devdb user -f /home/gx/code/shakespeare_character.sql | true
	docker-compose exec db psql devdb user -f /home/gx/code/shakespeare_paragraph.sql | true
	docker-compose exec db psql devdb user -f /home/gx/code/shakespeare_character_work.sql

.PHONY: model-generate
model-generate: ## generate sqlalchemy models from database
	poetry run sqlacodegen --generator declarative postgresql://user:secret@0.0.0.0/devdb --outfile models.py --schemas shakespeare
