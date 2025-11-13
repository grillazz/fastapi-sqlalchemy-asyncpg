# Set the default goal to "help" so that running "make" without arguments will display the help message.
.DEFAULT_GOAL := help

# ====================================================================================
# HELP
# ====================================================================================
# This target uses a combination of egrep, sort, and awk to parse the Makefile itself
# and generate a formatted help message. It looks for lines containing '##' and
# uses the text that follows as the help description for the target.
.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ====================================================================================
# DOCKER COMPOSE MANAGEMENT
# ====================================================================================
.PHONY: docker-build
docker-build:	## Build project Docker images using compose
	docker compose build

.PHONY: docker-up
docker-up:	## Run project with compose
	docker compose up --remove-orphans

.PHONY: docker-clean
docker-clean: ## Clean and reset project containers and volumes
	docker compose down -v --remove-orphans | true
	docker compose rm -f | true
	docker volume ls -q | grep panettone_postgres_data | xargs -r docker volume rm | true

# ====================================================================================
# DATABASE MIGRATIONS
# ====================================================================================
.PHONY: docker-apply-db-migrations
docker-apply-db-migrations: ## Apply alembic migrations to the database schema
	docker compose run --rm api1 alembic upgrade head

.PHONY: docker-create-db-migration
docker-create-db-migration:  ## Create a new alembic database migration. Example: make docker-create-db-migration msg="add users table"
	docker compose up -d postgres | true
	docker compose run --no-deps api1 alembic revision --autogenerate -m "$(msg)"

# ====================================================================================
# TESTING
# ====================================================================================
.PHONY: docker-test
docker-test:	## Run project tests
	docker compose -f compose.yml -f test-compose.yml  run --rm api1 pytest tests --durations=0 -vv

.PHONY: docker-test-snapshot
docker-test-snapshot:	## Run project tests and update snapshots
	docker compose -f compose.yml -f test-compose.yml  run --rm api1 pytest tests --inline-snapshot=fix

# ====================================================================================
# CODE QUALITY & LINTING
# ====================================================================================
.PHONY: safety
safety:	## Check for insecure dependencies
	docker compose run --rm api1 safety check

.PHONY: py-upgrade
py-upgrade:	## Upgrade Python syntax to a newer version
	pyupgrade --py313-plus `find app -name "*.py"`

.PHONY: lint
lint:  ## Lint and format project code
	uv run ruff check --fix .

# ====================================================================================
# DOCKER IMAGE BUILDING
# ====================================================================================
.PHONY: slim-build
slim-build: ## Build smaller and more secure Docker images with docker-slim
	docker-slim build --compose-file docker-compose.yml --target-compose-svc api1 --dep-include-target-compose-svc-deps true --http-probe-exec api1 fastapi-sqlalchemy-asyncpg_api1:latest

# ====================================================================================
# DATABASE SEEDING
# ====================================================================================
.PHONY: docker-feed-database
docker-feed-database: ## Create database objects and insert seed data
	docker compose exec postgres psql devdb devdb -f /home/gx/code/shakespeare_work.sql | true
	docker compose exec postgres psql devdb devdb -f /home/gx/code/shakespeare_chapter.sql | true
	docker compose exec postgres psql devdb devdb -f /home/gx/code/shakespeare_wordform.sql | true
	docker compose exec postgres psql devdb devdb -f /home/gx/code/shakespeare_character.sql | true
	docker compose exec postgres psql devdb devdb -f /home/gx/code/shakespeare_paragraph.sql | true
	docker compose exec postgres psql devdb devdb -f /home/gx/code/shakespeare_character_work.sql

# ====================================================================================
# MODEL GENERATION
# ====================================================================================
.PHONY: model-generate
model-generate: ## Generate SQLAlchemy models from the database schema
	poetry run sqlacodegen --generator declarative postgresql://devdb:secret@0.0.0.0/devdb --outfile models.py --schemas shakespeare --options nobidi

# ====================================================================================
# ALTERNATIVE RUNTIMES
# ====================================================================================
.PHONY: docker-up-granian
docker-up-granian: ## Run project with compose and the Granian web server
	docker compose -f granian-compose.yml up --remove-orphans

.PHONY: docker-up-valkey
docker-up-valkey: ## Run project with compose and Valkey
	docker compose -f valkey-compose.yml up --remove-orphans
