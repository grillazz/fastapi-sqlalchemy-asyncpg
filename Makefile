.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build:	## Build project with compose
	docker-compose build

.PHONY: up
up:	## Run project with compose
	docker-compose up --remove-orphans

.PHONY: down
down: ## Reset project containers with compose
	docker-compose down

.PHONY: lock
lock:	## Refresh pipfile.lock
	pipenv lock --pre

.PHONY: requirements
requirements:	## Refresh requirements.txt from pipfile.lock
	pipenv lock -r > requirements.txt

.PHONY: test
test:	## Run project tests
	docker-compose run --rm app pytest

.PHONY: safety
safety:	## Check project and dependencies with safety https://github.com/pyupio/safety
	docker-compose run --rm app safety check

.PHONY: lint
lint:  ## Lint project code.
	isort .
	black --fast --line-length=120 .
	mypy --ignore-missing-imports the_app
	flake8 --config .flake8 .

.PHONY: secret
secret: ## Generate random secret.
	openssl rand -hex 32
