PY ?= python3
CARTCAST = $(PY) -m cartcast
export PYTHONPATH := src

.DEFAULT_GOAL := help
.PHONY: help install sample data validate build build-sample serve test lint format check clean demo

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n",$$1,$$2}'

install: ## Install the package and dev tools (editable)
	$(PY) -m pip install -e ".[dev]"

sample: ## Regenerate the offline sample dataset in data/sample/
	$(PY) scripts/make_sample_data.py

data: ## Download live StatCan + City of Calgary data into data/raw/
	$(CARTCAST) fetch

validate: ## Check basket/swap product names against live data
	$(CARTCAST) validate

build: ## Build the dashboard from live data (run `make data` first)
	$(CARTCAST) build

build-sample: ## Build the dashboard from sample data (works offline)
	$(CARTCAST) build --sample

serve: ## Preview the built dashboard at http://localhost:8000
	$(CARTCAST) serve

demo: build-sample serve ## One command for the in-class live demo (offline-safe)

test: ## Run the test suite
	$(PY) -m pytest

lint: ## Lint with ruff
	ruff check .
	ruff format --check .

format: ## Auto-format with ruff
	ruff format .
	ruff check --fix .

check: lint test build-sample ## Everything CI runs

clean: ## Remove build output and downloaded data
	rm -rf site data/processed/*.json .pytest_cache .ruff_cache
	find data/raw -type f ! -name '.gitkeep' -delete
