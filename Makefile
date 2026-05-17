.PHONY: help up down build logs test clean

help:
	@echo "Available commands:"
	@echo "  make up      - Start the entire DevOps stack (App, DB, Redis, Nginx, Prometheus, Grafana)"
	@echo "  make down    - Stop all containers"
	@echo "  make build   - Rebuild the web application image"
	@echo "  make logs    - View logs of all containers"
	@echo "  make test    - Run pytest locally (requires virtual env)"
	@echo "  make clean   - Remove all stopped containers, networks, and unused images"

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

test:
	pytest tests/

clean:
	docker system prune -f
