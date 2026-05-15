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
