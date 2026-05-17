<<<<<<< HEAD
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
=======
.PHONY: help install test lint format run docker-build docker-up docker-down clean

help:
	@echo "Targets: install | test | lint | format | run | docker-build | docker-up | docker-down | clean"

install:
	pip install -r requirements-dev.txt

test:
	pytest tests/ --cov=website --cov=app --cov-report=term-missing --cov-fail-under=85

lint:
	ruff check website app.py wsgi.py tests
	ruff format --check website app.py wsgi.py tests

format:
	ruff format website app.py wsgi.py tests
	ruff check --fix website app.py wsgi.py tests

run:
	python app.py

docker-build:
	docker build -t website-cicd-pipeline:latest .

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

clean:
	rm -rf .pytest_cache __pycache__ website/__pycache__ tests/__pycache__ .coverage coverage.xml htmlcov
>>>>>>> 5961f6c04d0ae3859ddf1b2cdb3b470b10b1b79f
