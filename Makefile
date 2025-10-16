.PHONY: up up-seed down logs rebuild

up:
	docker compose up --build

up-seed:
	SEED=1 docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

rebuild:
	docker compose build --no-cache
