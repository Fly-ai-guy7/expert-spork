.PHONY: dev seed test test-backend test-frontend migrate upgrade pdf-sample clean lint format

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
