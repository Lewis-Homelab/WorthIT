# Makefile shortcuts — config from config.env (committed). Optional secrets in .env.

COMPOSE_ENV := --env-file config.env $(if $(wildcard .env),--env-file .env,)

.PHONY: dev test build deploy init

dev:
	docker compose $(COMPOSE_ENV) up --build

test:
	uv run pytest

build:
	docker compose $(COMPOSE_ENV) build

deploy:
	./scripts/deploy.sh

# Initialize a new project: make init APP=my-api PORT=8080
init:
	./scripts/init-project.sh $(APP) $(PORT)
