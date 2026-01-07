# Kibana Fixture Generator
# Generates test fixtures using Kibana's LensConfigBuilder API

IMAGE_NAME := kibana-fixture-generator
KIBANA_VERSION ?= v9.2.0
OUTPUT_DIR := $(shell pwd)/output
BASE_IMAGE ?= ghcr.io/strawgate/kb-yaml-to-lens/kibana-base:$(KIBANA_VERSION)

.PHONY: help all ci check fix test typecheck build build-no-cache build-from-source build-base pull-base run run-example shell test-import clean clean-image

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

all: build ## Default target: build Docker image

ci: build typecheck test ## Run CI checks (build + typecheck + test)
	@echo "✓ Fixture generator CI checks passed"

check: ci ## Alias for ci

fix: ## No linting to fix (placeholder for consistency)
	@echo "✓ No linting to fix for fixture generator"

typecheck: ## Run TypeScript type checking
	docker run --rm \
		-v $(shell pwd)/tsconfig.json:/kibana/tsconfig.json:ro \
		-v $(shell pwd)/examples:/kibana/examples:ro \
		-v $(shell pwd)/generator-utils.ts:/kibana/generator-utils.ts:ro \
		$(IMAGE_NAME):$(KIBANA_VERSION) \
		bash -c "tsc --noEmit --project tsconfig.json"

test: test-import ## Run tests

pull-base: ## Pull pre-built base image from GHCR
	docker pull $(BASE_IMAGE)

build: ## Build using pre-built base image from GHCR (~30 seconds)
	docker build \
		--build-arg KIBANA_VERSION=$(KIBANA_VERSION) \
		--build-arg BASE_IMAGE=$(BASE_IMAGE) \
		-t $(IMAGE_NAME):$(KIBANA_VERSION) \
		.

build-no-cache: ## Build without cache using pre-built base image
	docker build --no-cache \
		--build-arg KIBANA_VERSION=$(KIBANA_VERSION) \
		--build-arg BASE_IMAGE=$(BASE_IMAGE) \
		-t $(IMAGE_NAME):$(KIBANA_VERSION) \
		.

build-from-source: ## Build from source (Dockerfile.base, ~6 minutes)
	docker build \
		--build-arg KIBANA_VERSION=$(KIBANA_VERSION) \
		-f Dockerfile.base \
		-t $(IMAGE_NAME):$(KIBANA_VERSION) \
		.

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
		-v $(shell pwd)/generator-utils.js:/kibana/generator-utils.js:ro \
		-v $(shell pwd)/dataviews-mock.js:/kibana/dataviews-mock.js:ro \
		-v $(shell pwd)/generate-all.js:/kibana/generate-all.js:ro \
		-e NODE_OPTIONS="--max-old-space-size=8192" \
		-e KIBANA_VERSION=$(KIBANA_VERSION) \
		$(IMAGE_NAME):$(KIBANA_VERSION)

run-example: ## Run specific example (usage: make run-example EXAMPLE=metric-basic.js)
	@mkdir -p $(OUTPUT_DIR)
	docker run --rm \
		-v $(OUTPUT_DIR):/kibana/output \
		-v $(shell pwd)/examples:/kibana/examples:ro \
		-v $(shell pwd)/generator-utils.ts:/kibana/generator-utils.ts:ro \
		-v $(shell pwd)/generator-utils.js:/kibana/generator-utils.js:ro \
		-v $(shell pwd)/dataviews-mock.js:/kibana/dataviews-mock.js:ro \
		-e NODE_OPTIONS="--max-old-space-size=8192" \
		-e KIBANA_VERSION=$(KIBANA_VERSION) \
		$(IMAGE_NAME):$(KIBANA_VERSION) \
		tsx examples/$(EXAMPLE)

shell: ## Open a shell in the container for debugging
	docker run --rm -it \
		-v $(OUTPUT_DIR):/kibana/output \
		-v $(shell pwd)/examples:/kibana/examples:ro \
		-v $(shell pwd)/generator-utils.ts:/kibana/generator-utils.ts:ro \
		-v $(shell pwd)/generator-utils.js:/kibana/generator-utils.js:ro \
		-v $(shell pwd)/dataviews-mock.js:/kibana/dataviews-mock.js:ro \
		-v $(shell pwd)/generate-all.js:/kibana/generate-all.js:ro \
		-e NODE_OPTIONS="--max-old-space-size=8192" \
		$(IMAGE_NAME):$(KIBANA_VERSION) \
		/bin/bash

test-import: ## Test that @kbn/lens-embeddable-utils can be imported
	docker run --rm \
		$(IMAGE_NAME):$(KIBANA_VERSION) \
		tsx -e "import { LensConfigBuilder } from '@kbn/lens-embeddable-utils/config_builder'; console.log('LensConfigBuilder:', LensConfigBuilder)"

clean: ## Remove generated output files
	rm -rf $(OUTPUT_DIR)/*

clean-image: ## Remove the Docker image
	docker rmi $(IMAGE_NAME):$(KIBANA_VERSION) 2>/dev/null || true

