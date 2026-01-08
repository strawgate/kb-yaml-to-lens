# Kibana Fixture Generator
# Generates test fixtures using Kibana's LensConfigBuilder API

KIBANA_VERSION ?= v9.2.0
OUTPUT_DIR := $(shell pwd)/output
BASE_IMAGE ?= ghcr.io/strawgate/kb-yaml-to-lens/kibana-base:$(KIBANA_VERSION)

.PHONY: help all ci check fix test typecheck build-base pull run run-example shell test-import clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

all: pull ## Default target: pull pre-built base image

ci: pull typecheck test ## Run CI checks (pull + typecheck + test)
	@echo "✓ Fixture generator CI checks passed"

check: ci ## Alias for ci

fix: ## No linting to fix (placeholder for consistency)
	@echo "✓ No linting to fix for fixture generator"

typecheck: ## Run TypeScript type checking
	docker run --rm \
		-v $(shell pwd)/tsconfig.json:/kibana/tsconfig.json:ro \
		-v $(shell pwd)/examples:/kibana/examples:ro \
		-v $(shell pwd)/generator-utils.ts:/kibana/generator-utils.ts:ro \
		$(BASE_IMAGE) \
		bash -c "tsc --noEmit --project tsconfig.json"

test: ## Run tests
	@if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -qF "$(BASE_IMAGE)"; then \
		echo "⚠ Docker image not found, pulling..."; \
		$(MAKE) pull; \
	fi; \
	$(MAKE) test-import

pull: ## Pull pre-built base image from GHCR
	docker pull $(BASE_IMAGE)

build-base: ## Build base image locally (for testing base image changes)
	docker build \
		--build-arg KIBANA_VERSION=$(KIBANA_VERSION) \
		-f Dockerfile.base \
		-t $(BASE_IMAGE) \
		.

run: ## Generate all fixtures
	@mkdir -p $(OUTPUT_DIR)
	docker run --rm \
		-v $(OUTPUT_DIR):/kibana/output \
		-v $(shell pwd)/examples:/kibana/examples:ro \
		-v $(shell pwd)/generator-utils.ts:/kibana/generator-utils.ts:ro \
		-v $(shell pwd)/dataviews-mock.js:/kibana/dataviews-mock.js:ro \
		-v $(shell pwd)/generate-all.js:/kibana/generate-all.js:ro \
		-e NODE_OPTIONS="--max-old-space-size=8192" \
		-e KIBANA_VERSION=$(KIBANA_VERSION) \
		$(BASE_IMAGE) \
		tsx generate-all.js

run-example: ## Run specific example (usage: make run-example EXAMPLE=metric-basic.ts)
	@mkdir -p $(OUTPUT_DIR)
	docker run --rm \
		-v $(OUTPUT_DIR):/kibana/output \
		-v $(shell pwd)/examples:/kibana/examples:ro \
		-v $(shell pwd)/generator-utils.ts:/kibana/generator-utils.ts:ro \
		-v $(shell pwd)/dataviews-mock.js:/kibana/dataviews-mock.js:ro \
		-e NODE_OPTIONS="--max-old-space-size=8192" \
		-e KIBANA_VERSION=$(KIBANA_VERSION) \
		$(BASE_IMAGE) \
		tsx examples/$(EXAMPLE)

shell: ## Open a shell in the container for debugging
	docker run --rm -it \
		-v $(OUTPUT_DIR):/kibana/output \
		-v $(shell pwd)/examples:/kibana/examples:ro \
		-v $(shell pwd)/generator-utils.ts:/kibana/generator-utils.ts:ro \
		-v $(shell pwd)/dataviews-mock.js:/kibana/dataviews-mock.js:ro \
		-v $(shell pwd)/generate-all.js:/kibana/generate-all.js:ro \
		-e NODE_OPTIONS="--max-old-space-size=8192" \
		$(BASE_IMAGE) \
		/bin/bash

test-import: ## Test that @kbn/lens-embeddable-utils can be imported
	docker run --rm \
		$(BASE_IMAGE) \
		tsx -e "import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder'; console.log('LensConfigBuilder:', LensConfigBuilder)"

clean: ## Remove generated output files
	rm -rf $(OUTPUT_DIR)/*

