.PHONY: help up down restart ps logs logs-api logs-db test test-integration health migrate migration current shell db-shell check

help:
	@echo "ServerHub - comandos disponibles"
	@echo ""
	@echo "make up         Levanta los servicios"
	@echo "make down       Baja los servicios"
	@echo "make restart    Reinicia los servicios"
	@echo "make ps         Muestra estado de contenedores"
	@echo "make logs       Muestra logs de todos los servicios"
	@echo "make logs-api   Muestra logs de FastAPI"
	@echo "make logs-db    Muestra logs de PostgreSQL"
	@echo "make test       Ejecuta pytest"
	@echo "make health     Prueba /health"
	@echo "make migrate    Aplica migraciones Alembic"
	@echo "make migration  Genera migración automática"
	@echo "make current    Muestra revisión Alembic actual"
	@echo "make shell      Abre bash dentro del contenedor API"
	@echo "make db-shell   Abre psql dentro de PostgreSQL"
	@echo "make check      Verifica ServerHub antes de un commit"
	@echo "make test              Ejecuta tests normales"
	@echo "make test-integration  Ejecuta tests contra el servidor real"

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

ps:
	docker compose ps

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f api

logs-db:
	docker compose logs -f db

test:
	docker compose exec api python -m pytest -v -m "not integration"

health:
	curl http://127.0.0.1:8000/health

migrate:
	docker compose exec api alembic upgrade head

migration:
	@read -p "Nombre de la migración: " msg; \
	docker compose exec api alembic revision --autogenerate -m "$$msg"

current:
	docker compose exec api alembic current

shell:
	docker compose exec api bash

db-shell:
	docker compose exec db psql -U serverhub -d serverhub

check:
	@echo "=== ServerHub Check ==="
	@echo ""
	@echo "1. Estado de contenedores:"
	docker compose ps
	@echo ""
	@echo "2. Health de la API:"
	curl -f http://127.0.0.1:8000/health
	@echo ""
	@echo "3. Tests:"
	$(MAKE) test
	@echo ""
	@echo "=== Check completado correctamente ==="

test-integration:
	docker compose exec api python -m pytest -v -m integration
