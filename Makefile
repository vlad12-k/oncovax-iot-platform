COMPOSE_DEV  = docker compose -f infra/docker-compose.dev.yml
COMPOSE_PROD = docker compose -f infra/docker-compose.prod.yml

.PHONY: up down logs ps restart up-prod down-prod logs-prod smoke verify-local

up:
	$(COMPOSE_DEV) up -d

down:
	$(COMPOSE_DEV) down

logs:
	$(COMPOSE_DEV) logs -f --tail=200

ps:
	$(COMPOSE_DEV) ps

restart:
	$(COMPOSE_DEV) restart

up-prod:
	$(COMPOSE_PROD) up -d --build

down-prod:
	$(COMPOSE_PROD) down

logs-prod:
	$(COMPOSE_PROD) logs -f --tail=200

smoke:
	./scripts/smoke_test.sh

PYTHON ?= python3

.PHONY: test verify-static check-config

test:
	$(PYTHON) -m pytest -q

check-config:
	$(PYTHON) scripts/check_compose.py

verify-static: test check-config
	$(PYTHON) -m compileall -q services scripts tests
	bash -n scripts/smoke_test.sh

verify-local: verify-static
	$(COMPOSE_DEV) up -d --build --wait --wait-timeout 180
	./scripts/smoke_test.sh
	$(PYTHON) scripts/verify_pipeline.py
