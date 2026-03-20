COMPOSE_DEV  = docker compose -f infra/docker-compose.dev.yml
COMPOSE_PROD = docker compose -f infra/docker-compose.prod.yml

.PHONY: up down logs ps restart up-prod down-prod logs-prod smoke

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
