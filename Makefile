.PHONY: help dev-up dev-down backend frontend test lint migrate seed clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Docker ───────────────────────────────────────────────
dev-up: ## Start PostgreSQL + Redis (Docker)
	docker compose up -d
	@echo "⏳ Waiting for services..."
	@sleep 2
	@docker compose ps

dev-down: ## Stop Docker services
	docker compose down

dev-reset: ## Stop Docker + delete volumes (fresh DB)
	docker compose down -v

# ── Backend ──────────────────────────────────────────────
backend: ## Start FastAPI dev server
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-install: ## Install backend Python dependencies
	cd backend && pip install -e ".[dev]"

# ── Frontend ─────────────────────────────────────────────
frontend: ## Start React dev server
	cd frontend && npm run dev

frontend-install: ## Install frontend Node dependencies
	cd frontend && npm install

# ── Database ─────────────────────────────────────────────
migrate: ## Run Alembic migrations
	cd backend && alembic upgrade head

migrate-new: ## Create new migration (usage: make migrate-new msg="add_users_table")
	cd backend && alembic revision --autogenerate -m "$(msg)"

migrate-down: ## Rollback one migration
	cd backend && alembic downgrade -1

seed: ## Seed the database with initial data
	cd backend && python -m scripts.seed

# ── Celery ───────────────────────────────────────────────
worker: ## Start Celery worker
	cd backend && celery -A app.tasks.celery_app worker --loglevel=info

beat: ## Start Celery Beat scheduler
	cd backend && celery -A app.tasks.celery_app beat --loglevel=info

# ── Testing ──────────────────────────────────────────────
test: ## Run all tests (backend + frontend)
	cd backend && pytest -v
	cd frontend && npm run test -- --run

test-backend: ## Run backend tests only
	cd backend && pytest -v

test-frontend: ## Run frontend tests only
	cd frontend && npm run test -- --run

# ── Linting ──────────────────────────────────────────────
lint: ## Lint all code
	cd backend && ruff check . && ruff format --check .
	cd frontend && npm run lint

lint-fix: ## Auto-fix lint issues
	cd backend && ruff check --fix . && ruff format .
	cd frontend && npm run lint -- --fix

# ── Cleanup ──────────────────────────────────────────────
clean: ## Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/.ruff_cache frontend/dist
