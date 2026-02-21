.PHONY: build up down migrate seed logs shell-api shell-db test-api test-web test-e2e test

build:
	docker compose -f infra/docker-compose.yml build

up:
	docker compose -f infra/docker-compose.yml up -d

down:
	docker compose -f infra/docker-compose.yml down

migrate:
	docker compose -f infra/docker-compose.yml exec api alembic upgrade head

seed:
	docker compose -f infra/docker-compose.yml exec api python /app/scripts/seed_demo.py

logs:
	docker compose -f infra/docker-compose.yml logs -f

shell-api:
	docker compose -f infra/docker-compose.yml exec api bash

shell-db:
	docker compose -f infra/docker-compose.yml exec db psql -U appuser -d meetingmemo

# ── Testing ───────────────────────────────────────────────────────────────────
# Requires the Docker stack to be running: make up
# The test DB must exist: make shell-db → CREATE DATABASE meetingmemo_test;

test-api:
	docker compose -f infra/docker-compose.yml exec api python -m pytest tests/ -v

test-web:
	cd apps/web && npm run test

test-e2e:
	cd apps/web && npx playwright test

# Run backend + frontend unit tests (not E2E — those require the full stack)
test: test-api test-web
