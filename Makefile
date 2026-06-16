# Atajos de desarrollo. En Windows usa Git Bash/WSL, o copia los comandos a PowerShell.
.DEFAULT_GOAL := help
COMPOSE := docker compose
PROD := docker compose -f docker-compose.yml -f docker-compose.prod.yml

.PHONY: help dev dev-down prod prod-down logs seed ingest test lint fmt build

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

dev: ## Levanta el entorno de DESARROLLO (hot-reload + Adminer)
	$(COMPOSE) up --build

dev-down: ## Detiene el entorno de desarrollo
	$(COMPOSE) down

prod: ## Levanta el entorno de PRODUCCIÓN en segundo plano
	$(PROD) up -d --build

prod-down: ## Detiene el entorno de producción
	$(PROD) down

logs: ## Muestra los logs de la app
	$(COMPOSE) logs -f app

seed: ## Siembra las reservas de ejemplo
	$(COMPOSE) exec app python -m scripts.seed_db

ingest: ## Indexa las políticas del hotel (RAG)
	$(COMPOSE) exec app python -m scripts.ingest_policies --force

test: ## Ejecuta los tests
	pytest -q

lint: ## Linter (ruff)
	ruff check app scripts tests

fmt: ## Formatea el código (ruff)
	ruff format app scripts tests

build: ## Construye la imagen de la app
	$(COMPOSE) build
