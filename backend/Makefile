PY := python
PIP := $(PY) -m pip
PORT ?= 3000

.PHONY: help install dev-install fmt lint lint-fix type test run run-gunicorn clean

help:
	@echo "Targets:"
	@echo "  install       - install prod requirements"
	@echo "  dev-install   - install prod + dev requirements"
	@echo "  fmt           - run black formatter"
	@echo "  lint          - run ruff linter"
	@echo "  lint-fix      - run ruff with --fix"
	@echo "  type          - run mypy type checker"
	@echo "  test          - run pytest suite"
	@echo "  run           - start Flask dev server on port $(PORT)"
	@echo "  run-gunicorn  - start with gunicorn on port $(PORT)"
	@echo "  speed         - GET current /speed state"
	@echo "  speed-fast    - set speed mode=fast"
	@echo "  speed-slow    - set speed mode=slow"
	@echo "  speed-normal  - set speed mode=normal"

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

test:
	$(PY) -m pytest ./tests

run:
	$(PY) -m flask --app ./src/app run -p $(PORT)

run-gunicorn:
	gunicorn 'app:app' -b 0.0.0.0:$(PORT) --chdir ./src

speed:
	$(PY) ./scripts/speed.py --base-url http://localhost:$(PORT)

speed-fast:
	$(PY) ./scripts/speed.py fast --base-url http://localhost:$(PORT)

speed-slow:
	$(PY) ./scripts/speed.py slow --base-url http://localhost:$(PORT)

speed-normal:
	$(PY) ./scripts/speed.py normal --base-url http://localhost:$(PORT)
