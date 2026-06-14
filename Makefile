# Makefile shortcuts — config from config.env (committed). Optional secrets in .env.

COMPOSE_ENV := --env-file config.env $(if $(wildcard .env),--env-file .env,)

.PHONY: dev test build deploy down logs api-shell db-shell

dev:
	docker compose $(COMPOSE_ENV) up --build

down:
	docker compose $(COMPOSE_ENV) down

logs:
	docker compose $(COMPOSE_ENV) logs -f

test:
	uv run pytest

build:
	docker compose $(COMPOSE_ENV) build

deploy:
	./scripts/deploy.sh

api-shell:
	docker compose $(COMPOSE_ENV) exec api bash

db-shell:
	docker compose $(COMPOSE_ENV) exec db psql -U $$(grep '^POSTGRES_USER=' config.env | cut -d= -f2) -d $$(grep '^POSTGRES_DB=' config.env | cut -d= -f2)
