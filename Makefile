.PHONY: help setup format lint test validate evaluate forecast

PYTHON := python

help:
	@echo "Common targets:"
	@echo "  setup      - create venv and install requirements"
	@echo "  format     - run black and ruff fix"
	@echo "  lint       - run ruff check"
	@echo "  test       - run pytest"
	@echo "  forecast   - produce baseline submission CSV"
	@echo "  validate   - validate a submission CSV"
	@echo "  evaluate   - evaluate a submission against ground truth"

setup:
	$(PYTHON) -m venv .venv && . .venv/bin/activate && \
	python -m pip install -U pip && \
	pip install -r requirements.txt

format:
	black src tests
	ruff check --fix src tests

lint:
	ruff check src tests

test:
	PYTHONPATH=. pytest -q

forecast:
	$(PYTHON) -m src.forecast

validate:
	@if [ -z "$$FILE" ]; then echo "Usage: make validate FILE=path/to/submission.csv"; exit 1; fi; \
	$(PYTHON) -m src.validate_submission --file $$FILE

evaluate:
	@if [ -z "$$SUB" ] || [ -z "$$TRUTH" ]; then echo "Usage: make evaluate SUB=path/to/submission.csv TRUTH=path/to/truth.csv"; exit 1; fi; \
	$(PYTHON) -m src.evaluate --submission $$SUB --truth $$TRUTH

