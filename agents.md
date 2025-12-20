# Repository Summary: kb-yaml-to-lens

**Project Description:** Dashboard Compiler - Simplifies Kibana dashboard creation by converting human-readable YAML into complex native Kibana dashboard JSON format.

**Language:** Python
**Default Branch:** main
**Created:** 2025-04-23
**Last Updated:** 2025-12-20

---

## Architecture Overview

The `kb-yaml-to-lens` project, also known as the "Dashboard Compiler," aims to simplify Kibana dashboard creation by converting a human-readable YAML representation into the complex native Kibana dashboard JSON format. It uses a layered architecture:

1. **YAML Loading & Parsing:** `PyYAML` parses YAML config files into Python dictionaries (see `architecture.md` - YAML Loading & Parsing section).
2. **Pydantic Model Representation:** Pydantic models (e.g., `Dashboard` in `dashboard_compiler/dashboard/config.py`) define the YAML schema, handling data validation and dynamic instantiation of panel subclasses (see `architecture.md` - Pydantic Model Representation section).
3. **JSON Compilation:** Each Pydantic model includes a `to_json()` method (or `model_dump_json` for view models) to convert its data into the corresponding Kibana JSON structure, orchestrated by the top-level `Dashboard` model (see `architecture.md` - JSON Compilation section).

The primary goal is maintainability and abstraction from Kibana's native JSON complexity (see `architecture.md` - Project Goals).

---

## Code Style & Conventions

- **Python Formatting:** Line length is set to 140 characters, enforced by Ruff (see `pyproject.toml` - line-length setting in tool.ruff section).
- **Pydantic Models:** Configuration models (`BaseCfgModel`) are strict, validate defaults, use enum values, are frozen (immutable), use attribute docstrings for descriptions, and serialize by alias (see `dashboard_compiler/shared/model.py` - BaseCfgModel class definition). View models (`BaseVwModel`) extend this, adding a custom serializer to omit fields with `OmitIfNone` metadata if their value is `None` (see `dashboard_compiler/shared/view.py` - BaseVwModel class definition).
- **Testing:** `pytest` is used for testing, with `pytest-asyncio` configured for `function` scope and `auto` mode (see `pyproject.toml` - tool.pytest.ini_options section). `syrupy` with `JSONSnapshotExtension` is used for snapshot testing, freezing timestamps for consistency (see `tests/conftest.py` - snapshot_json fixture).
- **Docstrings:** Pydantic models leverage attribute docstrings for field descriptions (see `dashboard_compiler/shared/model.py` - BaseCfgModel class).

---

## Key Directories & Entry Points

| Directory | Why it matters |
|---|---|
| `dashboard_compiler/` | Contains the core logic for YAML parsing, Pydantic model definitions, and JSON compilation. |
| `dashboard_compiler/dashboard/` | Defines the top-level `Dashboard` configuration (config.py) and its compilation logic (compile.py). |
| `dashboard_compiler/panels/` | Houses definitions and compilation logic for various Kibana panel types (e.g., `markdown`, `links`, `charts`). |
| `dashboard_compiler/panels/charts/` | Specific compilation logic for Lens and ESQL chart types (e.g., `metric`, `pie`, `xy`). |
| `scripts/` | Contains utility scripts for compiling configurations to NDJSON (`compile_configs_to_ndjson.py`) and generating documentation (`compile_docs.py`). |
| `inputs/` | Example YAML dashboard configurations for compilation. |
| `test/` | Contains unit and integration tests, including snapshot tests for generated Kibana JSON. |
| `dashboard_compiler/dashboard_compiler.py` | Main entry point for loading, rendering, and dumping dashboard configurations (load, render, dump functions). |

---

## Quick Recipes

| Command | Description |
|---|---|
| Install dependencies | `uv sync` |
| Run tests | `uv run pytest` |
| Run specific test | `uv run pytest test/dashboards/test_dashboards.py` |
| Compile all input YAMLs to NDJSON | `uv run python scripts/compile_configs_to_ndjson.py` |
| Compile documentation | `uv run python scripts/compile_docs.py` |
| Format code | `uv run ruff format .` |
| Lint code | `uv run ruff check .` |

---

## Dependencies & Compatibility

- **Runtime Dependencies:** Python `>=3.12`, `PyYAML >=6.0` for YAML parsing, `Pydantic >=2.11.3` for schema definition and validation (see `pyproject.toml` - project.dependencies section).
- **Toolchain:** Python 3.12+ is required. Project uses `uv` for dependency management (see `pyproject.toml`).
- **Testing/Dev Dependencies:** `pytest >=7.0`, `syrupy >=4.9.1` for snapshot testing, `pytest-freezer >=0.4.9` for time-sensitive tests, `deepdiff >=8.4.2` for comparing complex data structures, and `ruff >=0.11.6` for linting and formatting (see `pyproject.toml` - project.optional-dependencies.dev section).

---

## Unique Workflows

- **Dashboard Compilation:** YAML configuration files (e.g., `inputs/*.yaml`, `test/dashboards/scenarios/*.yaml`) are loaded, validated against Pydantic models, and then compiled into Kibana dashboard JSON. The `dashboard_compiler.dashboard_compiler.render` function orchestrates this process (see `dashboard_compiler/dashboard_compiler.py` - render function).
- **Documentation Generation:** A script (`scripts/compile_docs.py`) automatically compiles all markdown files within the `dashboard_compiler/` directory into a single `yaml_reference.md` file at the repository root. It prioritizes `dashboard/dashboard.md` and then sorts others by path (see `scripts/compile_docs.py` - main compilation logic).
- **NDJSON Output:** Compiled Kibana dashboards can be output as NDJSON (Newline Delimited JSON) files, suitable for direct import into Kibana. The `scripts/compile_configs_to_ndjson.py` script handles this, processing YAML files from `inputs/` and `test/dashboards/scenarios/` (see `scripts/compile_configs_to_ndjson.py`).

---

## API Surface Map

The project's primary "API" is its YAML configuration schema for defining Kibana dashboards.

- **YAML Schema:** The root element is `dashboard`, which defines global settings, queries, filters, controls, and a list of `panels` (see `yaml_reference.md` - Dashboard section).
- **Panel Types:** Supported panel types include `markdown` (see `quickstart.md` - Markdown panel examples), `lens` (see `quickstart.md` - Lens panel examples), `links`, `search`, and various chart types (e.g., `metric`, `pie`, `xy`) (see `dashboard_compiler/panels/types.py` and `dashboard_compiler/panels/charts/config.py`).
- **Compilation Functions:** The core programmatic interface is exposed through `dashboard_compiler.dashboard_compiler.load` (loads YAML), `dashboard_compiler.dashboard_compiler.render` (compiles to Kibana JSON view model), and `dashboard_compiler.dashboard_compiler.dump` (dumps Pydantic config to YAML) (see `dashboard_compiler/dashboard_compiler.py`).
- **Where to learn more:** Detailed YAML configuration options for each component (dashboard, panels, controls, filters, queries) are documented in `yaml_reference.md` and individual `config.md` files within the `dashboard_compiler/` subdirectories (see `quickstart.md` - Additional Resources).

---

## Onboarding Steps

- **Understand Core Architecture:** Review `architecture.md` to grasp the overall design and data flow.
- **Explore YAML Schema:** Read `yaml_reference.md` and `quickstart.md` for a comprehensive understanding of the YAML configuration structure and examples.
- **Examine Pydantic Models:** Dive into `dashboard_compiler/**/config.py` files to see the definitive source of truth for configuration options, types, and validation rules.
- **Trace Compilation Logic:** Follow the `compile_dashboard` function in `dashboard_compiler/dashboard/compile.py` to understand how YAML models are transformed into Kibana JSON view models.
- **Run Tests:** Execute `uv run pytest` and inspect the `test/__snapshots__/` directory to see examples of generated Kibana JSON for various dashboard configurations.

---

## Getting Unstuck

- **Pydantic Validation Errors:** If YAML parsing or model validation fails, check the `strict=True` and `extra='forbid'` settings in `dashboard_compiler/shared/model.py` (search for BaseCfgModel class). These ensure strict adherence to the defined schema, so any unexpected fields or incorrect types will raise an error.
- **Snapshot Test Failures:** If snapshot tests (`uv run pytest`) fail, it usually means the generated Kibana JSON has changed. Review the `deepdiff` output to understand the differences and update the snapshots if the change is intentional (see `tests/conftest.py` - snapshot_json fixture).
- **Documentation Generation Issues:** If `yaml_reference.md` is not updating correctly, ensure `scripts/compile_docs.py` is run and check for warnings about missing markdown files.
