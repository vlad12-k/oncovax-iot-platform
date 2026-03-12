COMPOSE_DEV = docker compose -f infra/docker-compose.dev.yml

.PHONY: up down logs ps restart

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
