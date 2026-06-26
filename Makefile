# Makefile shortcuts — config from config.env (committed). Optional secrets in .env.

COMPOSE_ENV := --env-file config.env $(if $(wildcard .env),--env-file .env,)

COMPOSE_DEV := -f compose.yaml -f compose.dev.yaml

.PHONY: dev test build deploy down logs api-shell db-shell dev-reset-web

dev:
	docker compose $(COMPOSE_ENV) $(COMPOSE_DEV) up --build

# Fix "next: not found" — wipes the stale frontend node_modules volume
dev-reset-web:
	docker compose $(COMPOSE_ENV) $(COMPOSE_DEV) down
	docker volume rm -f worthit_web_node_modules 2>/dev/null || true
	docker compose $(COMPOSE_ENV) $(COMPOSE_DEV) up --build

down:
	docker compose $(COMPOSE_ENV) $(COMPOSE_DEV) down

logs:
	docker compose $(COMPOSE_ENV) $(COMPOSE_DEV) logs -f

test:
	uv run pytest

build:
	docker compose $(COMPOSE_ENV) $(COMPOSE_DEV) build

deploy:
	./scripts/deploy.sh

api-shell:
	docker compose $(COMPOSE_ENV) exec api bash

db-shell:
	docker compose $(COMPOSE_ENV) exec db psql -U $$(grep '^POSTGRES_USER=' config.env | cut -d= -f2) -d $$(grep '^POSTGRES_DB=' config.env | cut -d= -f2)
