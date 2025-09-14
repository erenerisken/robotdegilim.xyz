PY := python
PIP := $(PY) -m pip
PORT ?= 3000

.PHONY: help install dev-install fmt lint lint-fix type run run-gunicorn clean

help:
	@echo "Targets:"
	@echo "  install       - install prod requirements"
	@echo "  dev-install   - install prod + dev requirements"
	@echo "  fmt           - run black formatter"
	@echo "  lint          - run ruff linter"
	@echo "  lint-fix      - run ruff with --fix"
	@echo "  type          - run mypy type checker"
	@echo "  run           - start Flask dev server on port $(PORT)"
	@echo "  run-gunicorn  - start with gunicorn on port $(PORT)"

install:
	$(PIP) install -r ./requirements.txt

dev-install: install
	$(PIP) install -r ./requirements-dev.txt

fmt:
	black ./src

lint:
	ruff check ./src

lint-fix:
	ruff check --fix ./src

type:
	mypy ./src

run:
	$(PY) -m flask --app ./src/app run -p $(PORT)

run-gunicorn:
	gunicorn 'app:app' -b 0.0.0.0:$(PORT) --chdir ./src

