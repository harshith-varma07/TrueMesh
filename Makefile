.PHONY: help install start stop restart logs clean test build

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install dependencies locally
	pip install -r requirements.txt

start: ## Start all services with Docker Compose
	docker-compose up -d
	@echo "✅ TrueMesh is running at http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"

stop: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## View application logs
	docker-compose logs -f app

logs-all: ## View all service logs
	docker-compose logs -f

clean: ## Stop services and remove volumes
	docker-compose down -v

build: ## Build Docker images
	docker-compose build

test: ## Run tests (when implemented)
	pytest

db-migrate: ## Run database migrations
	alembic upgrade head

db-rollback: ## Rollback last migration
	alembic downgrade -1

db-create-migration: ## Create a new migration (use with MESSAGE="description")
	alembic revision --autogenerate -m "$(MESSAGE)"

verify: ## Verify implementation structure
	python3 verify_implementation.py

dev: ## Run in development mode (without Docker)
	python main.py
