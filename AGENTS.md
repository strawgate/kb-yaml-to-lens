# Repository Summary: kb-yaml-to-lens

**Project Description:** Dashboard Compiler - Simplifies Kibana dashboard creation by converting human-readable YAML into complex native Kibana dashboard JSON format.

**Language:** Python
**Default Branch:** main
**Created:** 2025-04-23
**Last Updated:** 2025-12-20

---

## Development Workflow

### Required Pre-commit Checks

Before committing:

1. `make lint` - Ruff formatting and linting
2. `make test` - All tests pass
3. Type checking via basedpyright (runs in CI)

Or run together: `make check`

### Testing Requirements

- Fixture-based approach (Pattern 3) preferred for new tests
- Test files in `test/` mirror `src/dashboard_compiler/` structure
- Snapshots freeze timestamps using pytest-freezer
- Update snapshots when intentional changes occur

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

## Common Pitfalls

### Pydantic Model Conventions

**Configuration models** (`BaseCfgModel` in `dashboard_compiler/shared/model.py`):
- `strict=True`, `extra='forbid'`, `frozen=True`, `validate_default=True`
- Use attribute docstrings for field descriptions

**View models** (`BaseVwModel` in `dashboard_compiler/shared/view.py`):
- Custom serializer omits fields with `OmitIfNone` metadata when value is `None`
- May narrow types in subclasses (e.g., `str` -> `Literal['value']`)
- `reportIncompatibleVariableOverride = false` in basedpyright config allows this

### Testing Patterns

- **Preferred**: Pattern 3 (fixture-based with inline-snapshot)
- Test fixtures in `test/conftest.py` provide `snapshot_json` with frozen timestamps
- Each test independent and runnable

### Type Checking

- **Mode**: `standard` (basedpyright)
- **Python version**: 3.12+
- Pydantic view models have special override allowances

### Tool Usage

- **Dependency manager**: `uv` (not Poetry)
- **Line length**: 140 characters
- **Docstring coverage**: 80% threshold (checked by CodeRabbit)

---

## Working with Code Review Feedback

### For AI Coding Agents (Claude)

#### 1. Triage Before Acting

Categorize feedback:
- **Critical**: Security issues, data corruption, type safety violations, test failures
- **Important**: Error handling, performance, missing tests, type annotations
- **Optional**: Style preferences, minor refactors, conflicting patterns

#### 2. Evaluate Against Existing Patterns

Before accepting suggestions:
- Search codebase for similar patterns
- Check how other panels/compilers handle similar cases
- Preserve consistency over isolated best practices

#### 3. Consider Context and Scope

Requirements vary by code type:
- **Compilation logic**: Prioritize correctness, type safety
- **CLI code**: Focus on user experience, error messages, Rich formatting
- **Test code**: Emphasize clarity, coverage, fixture patterns
- **Documentation**: Prioritize accuracy and completeness

#### 4. Verify Completion

Before claiming work is ready:
- All critical issues addressed or documented as out-of-scope
- All important issues addressed or explicitly deferred with rationale
- `make check` passes (lint + test)
- Type checking passes (basedpyright in CI)
- Tests pass with updated snapshots if needed

#### 5. Document Deferrals

If feedback isn't implemented, explain why:
- Conflicts with established pattern (cite similar code)
- Out of scope for component purpose
- Trade-off not worth the complexity

### For AI Code Reviewers (CodeRabbit)

#### Project-Specific Patterns

- Test patterns: Pattern 3 (fixture-based with inline-snapshot) preferred
- Pydantic view models may narrow types in subclasses - intentional
- CLI output uses Rich/rich-click
- Documentation auto-generated from markdown files

#### Prioritization Guidance

Categorize by severity:
- **Critical**: Type safety violations, security issues, data corruption, test failures
- **Important**: Missing error handling, performance issues, missing tests
- **Minor/Optional**: Style preferences, optimizations, refactoring

#### Pattern Consistency

Before suggesting changes:
- Check if similar patterns exist in other compile.py files
- If pattern exists across multiple panels/charts, likely intentional

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

## Make Commands Reference

| Command | Purpose |
|---------|---------|
| `make help` | Show all available commands |
| `make install` | Install all dependencies via uv sync |
| `make check` | Run lint + test + test-smoke |
| `make test` | Run full pytest suite (verbose) |
| `make test-smoke` | Basic smoke test |
| `make lint` | Run autocorrect + format |
| `make autocorrect` | Run ruff check --fix |
| `make format` | Run ruff format |
| `make compile` | Compile YAML dashboards to NDJSON |
| `make upload` | Compile and upload to Kibana |
| `make clean` | Remove cache and temp files |
| `make clean-full` | Clean all including .venv |
| `make inspector` | Run MCP Inspector |
| `make setup` | Full environment setup (installs uv) |
| `make update-deps` | Update all dependencies |

### Common Workflows

**Development cycle:**
```bash
make install        # First time setup
# Make changes
make check          # Before committing
```

**Testing specific changes:**
```bash
make test           # Full suite
uv run pytest test/panels/test_metrics.py  # Specific file
```

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

## CI/CD

GitHub Actions workflows in `.github/workflows/`:

- **test.yml**: Runs tests, linting, and type checking
- **claude-on-mention.yml**: Claude Code assistant (can make PRs when @claude mentioned)
- **claude-on-open-label.yml**: Claude triage assistant (read-only analysis on labeled issues)

### Workflow Modification Restrictions

**Claude cannot modify files in `.github/workflows/`** - only GitHub Copilot has permissions to change workflow files. If Claude attempts to commit changes to workflow files, the commit will be rejected with an error.

If workflow changes are needed, either:
- Use GitHub Copilot to make the changes
- Manually edit workflow files outside of Claude's scope

### Pre-commit Expectations

CI will fail if:
- Ruff linting fails
- Tests fail
- Type checking fails (basedpyright standard mode)
- Docstring coverage below 80% (CodeRabbit warning)

Run `make check` locally to catch issues before pushing.

---

## Radical Honesty

Agents should be honest when working with code review feedback:

- **Document unresolved items** and explain why they weren't addressed
- **Acknowledge uncertainty** - ask if unclear about patterns or requirements
- **Report problems** encountered during implementation
- **Share reasoning** for rejecting or deferring feedback
- **Admit limitations** if unable to verify fixes work correctly

**Never claim work is complete with unresolved critical or important issues.**
