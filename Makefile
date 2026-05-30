.PHONY: dev seed test test-backend test-frontend migrate upgrade pdf-sample clean lint format ci-backend ci-frontend pre-commit-install worker prod-build prod-up prod-down prod-logs backup-now

dev:
	docker-compose up --build

dev-detached:
	docker-compose up --build -d

down:
	docker-compose down

seed:
	docker-compose exec backend python -m app.corpus_loader

test: test-backend test-frontend

test-backend:
	docker-compose exec backend pytest -v

test-frontend:
	docker-compose exec frontend npm test -- --run

migrate:
	docker-compose exec backend alembic revision --autogenerate -m "$(m)"

upgrade:
	docker-compose exec backend alembic upgrade head

pdf-sample:
	./scripts/run_sample_case.sh

clean:
	docker-compose down -v
	rm -rf backend/__pycache__ frontend/node_modules frontend/dist

lint:
	docker-compose exec backend ruff check .
	docker-compose exec frontend npm run lint

format:
	docker-compose exec backend ruff format .

# --- No-docker targets (what CI runs) ---

ci-backend:
	cd backend && ruff check . && pytest -q --cov=app --cov-report=term --cov-fail-under=80

ci-frontend:
	cd frontend && (npm ci || npm install) && npm run lint --if-present && npm test -- --run && npm run build && node scripts/check-bundle-size.mjs

pre-commit-install:
	pip install pre-commit && pre-commit install

worker:
	docker-compose exec backend celery -A app.workers.celery_app worker --loglevel=info

# --- Production (docker-compose.prod.yml + .env.prod) ---

prod-build:
	docker compose -f docker-compose.prod.yml --env-file .env.prod build

prod-up:
	docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

prod-down:
	docker compose -f docker-compose.prod.yml --env-file .env.prod down

prod-logs:
	docker compose -f docker-compose.prod.yml --env-file .env.prod logs -f --tail=100

backup-now:
	docker compose -f docker-compose.prod.yml --env-file .env.prod exec backup /backup.sh
