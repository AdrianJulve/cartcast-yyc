PY ?= python3
CARTCAST = $(PY) -m cartcast
export PYTHONPATH := src

.DEFAULT_GOAL := help
.PHONY: help install sample data snapshot validate build build-sample serve test lint format check clean demo

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n",$$1,$$2}'

install: ## Install the package and development tools
	$(PY) -m pip install -e ".[dev]"

sample: ## Regenerate the offline sample dataset in data/sample/
	$(PY) scripts/make_sample_data.py

data: ## Download real data and update data/snapshot/
	$(CARTCAST) fetch

snapshot: ## Rebuild data/snapshot/ from files already in data/raw/
	$(CARTCAST) snapshot

validate: ## Check basket and substitution names against the snapshot
	$(CARTCAST) validate

build: ## Build the dashboard from the real-data snapshot
	$(CARTCAST) build

build-sample: ## Build the dashboard from sample data (works offline)
	$(CARTCAST) build --sample

serve: ## Preview the built dashboard at http://localhost:8000
	$(CARTCAST) serve

demo: build-sample serve ## Build with sample data and serve it (works offline)

test: ## Run the test suite
	$(PY) -m pytest

lint: ## Lint with ruff
	ruff check .
	ruff format --check .

format: ## Auto-format with ruff
	ruff format .
	ruff check --fix .

check: lint test build-sample ## Run the same checks as CI

clean: ## Remove build output and downloaded data
	rm -rf site data/processed/*.json .pytest_cache .ruff_cache
	find data/raw -type f ! -name '.gitkeep' -delete
