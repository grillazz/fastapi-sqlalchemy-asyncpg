.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: docker-build
docker-build:	## Build project with compose
	docker compose build

.PHONY: docker-up
docker-up:	## Run project with compose
	docker compose up --remove-orphans

.PHONY: docker-clean
docker-clean: ## Clean Reset project containers and volumes with compose
	docker compose down -v --remove-orphans | true
	docker compose rm -f | true
	docker volume rm panettone_postgres_data | true

.PHONY: docker-apply-db-migrations
docker-apply-db-migrations: ## apply alembic migrations to database/schema
	docker compose run --rm api1 alembic upgrade head

.PHONY: docker-create-db-migration
docker-create-db-migration:  ## Create new alembic database migration aka database revision. Example: make docker-create-db-migration msg="add users table"
	docker compose up -d postgres | true
	docker compose run --no-deps api1 alembic revision --autogenerate -m "$(msg)"

.PHONY: docker-test
docker-test:	## Run project tests
	docker compose -f compose.yml -f test-compose.yml  run --rm api1 pytest tests --durations=0 -vv

.PHONY: docker-test-snapshot
docker-test-snapshot:	## Run project tests with inline snapshot
	docker compose -f compose.yml -f test-compose.yml  run --rm api1 pytest tests --inline-snapshot=fix

.PHONY: safety
safety:	## Check project and dependencies with safety https://github.com/pyupio/safety
	docker compose run --rm api1 safety check

.PHONY: py-upgrade
py-upgrade:	## Upgrade project py files with pyupgrade library for python version 3.10
	pyupgrade --py313-plus `find api1 -name "*.py"`

.PHONY: lint
lint:  ## Lint project code.
	uv run ruff check --fix .

.PHONY: slim-build
slim-build: ## with power of docker-slim build smaller and safer images
	docker-slim build --compose-file docker-compose.yml --target-compose-svc api1 --dep-include-target-compose-svc-deps true --http-probe-exec api1 fastapi-sqlalchemy-asyncpg_api1:latest

.PHONY: docker-feed-database
docker-feed-database: ## create database objects and insert data
	docker compose exec postgres psql devdb devdb -f /home/gx/code/shakespeare_work.sql | true
	docker compose exec postgres psql devdb devdb -f /home/gx/code/shakespeare_chapter.sql | true
	docker compose exec postgres psql devdb devdb -f /home/gx/code/shakespeare_wordform.sql | true
	docker compose exec postgres psql devdb devdb -f /home/gx/code/shakespeare_character.sql | true
	docker compose exec postgres psql devdb devdb -f /home/gx/code/shakespeare_paragraph.sql | true
	docker compose exec postgres psql devdb devdb -f /home/gx/code/shakespeare_character_work.sql

.PHONY: model-generate
model-generate: ## generate sqlalchemy models from database
	poetry run sqlacodegen --generator declarative postgresql://devdb:secret@0.0.0.0/devdb --outfile models.py --schemas shakespeare --options nobidi

.PHONY: docker-up-granian
docker-up-granian: ## Run project with compose and granian
	docker compose -f granian-compose.yml up --remove-orphans

.PHONY: docker-up-valkey
docker-up-valkey: ## Run project with compose and valkey
	docker compose -f valkey-compose.yml up --remove-orphans
