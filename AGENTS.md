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

---

## Architecture Overview

Dashboard Compiler converts human-readable YAML into Kibana dashboard JSON using three layers:

1. **YAML Loading**: `PyYAML` parses YAML config files into Python dictionaries
2. **Pydantic Models**: Models in `src/dashboard_compiler/*/config.py` define schema, validate data, and handle panel type polymorphism
3. **JSON Compilation**: Each model's `to_json()` (or `model_dump_json`) method converts to Kibana JSON format

Goal: Maintainability and abstraction from Kibana's complex native JSON. See `architecture.md` for details.

---

## Code Style & Conventions

- **Line length**: 140 characters (Ruff enforced)
- **Config models** (`BaseCfgModel`): Strict, frozen, validate defaults, use attribute docstrings
- **View models** (`BaseVwModel`): Omit fields with `OmitIfNone` metadata when value is `None`
- **Docstrings**: Use attribute docstrings on Pydantic model fields

---

## Common Pitfalls

### Pydantic Model Conventions

**Configuration models** (`BaseCfgModel` in `src/dashboard_compiler/shared/model.py`):

- `strict=True`, `extra='forbid'`, `frozen=True`, `validate_default=True`
- Use attribute docstrings for field descriptions

**View models** (`BaseVwModel` in `src/dashboard_compiler/shared/view.py`):

- Custom serializer omits fields with `OmitIfNone` metadata when value is `None`
- May narrow types in subclasses (e.g., `str` -> `Literal['value']`)
- `reportIncompatibleVariableOverride = false` in basedpyright config allows this

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

- Pydantic view models may narrow types in subclasses - intentional design
- CLI output uses Rich/rich-click for formatting
- Documentation auto-generated from markdown files via `scripts/compile_docs.py`

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
| `src/dashboard_compiler/` | Contains the core logic for YAML parsing, Pydantic model definitions, and JSON compilation. |
| `src/dashboard_compiler/dashboard/` | Defines the top-level `Dashboard` configuration (config.py) and its compilation logic (compile.py). |
| `src/dashboard_compiler/panels/` | Houses definitions and compilation logic for various Kibana panel types (e.g., `markdown`, `links`, `charts`). |
| `src/dashboard_compiler/panels/charts/` | Specific compilation logic for Lens and ESQL chart types (e.g., `metric`, `pie`, `xy`). |
| `scripts/` | Contains utility scripts for compiling configurations to NDJSON (`compile_configs_to_ndjson.py`) and generating documentation (`compile_docs.py`). |
| `inputs/` | Example YAML dashboard configurations for compilation. |
| `tests/` | Contains unit and integration tests, including snapshot tests for generated Kibana JSON. |
| `src/dashboard_compiler/dashboard_compiler.py` | Main entry point for loading, rendering, and dumping dashboard configurations (load, render, dump functions). |

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
uv run pytest tests/panels/test_metrics.py  # Specific file
```

---

## Dependencies & Compatibility

- **Runtime Dependencies:** Python `>=3.12`, `PyYAML >=6.0` for YAML parsing, `Pydantic >=2.11.3` for schema definition and validation (see `pyproject.toml` - project.dependencies section).
- **Toolchain:** Python 3.12+ is required. Project uses `uv` for dependency management (see `pyproject.toml`).
- **Testing/Dev Dependencies:** `pytest >=7.0`, `syrupy >=4.9.1` for snapshot testing, `pytest-freezer >=0.4.9` for time-sensitive tests, `deepdiff >=8.4.2` for comparing complex data structures, and `ruff >=0.11.6` for linting and formatting (see `pyproject.toml` - project.optional-dependencies.dev section).

---

## Unique Workflows

- **Dashboard Compilation:** YAML configuration files (e.g., `inputs/*.yaml`, `tests/dashboards/scenarios/*.yaml`) are loaded, validated against Pydantic models, and then compiled into Kibana dashboard JSON. The `dashboard_compiler.dashboard_compiler.render` function orchestrates this process (see `src/dashboard_compiler/dashboard_compiler.py` - render function).
- **Documentation Generation:** A script (`scripts/compile_docs.py`) automatically compiles all markdown files within the `src/dashboard_compiler/` directory into a single `yaml_reference.md` file at the repository root. It prioritizes `dashboard/dashboard.md` and then sorts others by path (see `scripts/compile_docs.py` - main compilation logic).
- **NDJSON Output:** Compiled Kibana dashboards can be output as NDJSON (Newline Delimited JSON) files, suitable for direct import into Kibana. The `scripts/compile_configs_to_ndjson.py` script handles this, processing YAML files from `inputs/` and `tests/dashboards/scenarios/` (see `scripts/compile_configs_to_ndjson.py`).

---

## API Surface Map

The project's primary "API" is its YAML configuration schema for defining Kibana dashboards.

- **YAML Schema:** The root element is `dashboard`, which defines global settings, queries, filters, controls, and a list of `panels` (see `yaml_reference.md` - Dashboard section).
- **Panel Types:** Supported panel types include `markdown` (see `quickstart.md` - Markdown panel examples), `lens` (see `quickstart.md` - Lens panel examples), `links`, `search`, and various chart types (e.g., `metric`, `pie`, `xy`) (see `src/dashboard_compiler/panels/types.py` and `src/dashboard_compiler/panels/charts/config.py`).
- **Compilation Functions:** The core programmatic interface is exposed through `dashboard_compiler.dashboard_compiler.load` (loads YAML), `dashboard_compiler.dashboard_compiler.render` (compiles to Kibana JSON view model), and `dashboard_compiler.dashboard_compiler.dump` (dumps Pydantic config to YAML) (see `src/dashboard_compiler/dashboard_compiler.py`).
- **Where to learn more:** Detailed YAML configuration options for each component (dashboard, panels, controls, filters, queries) are documented in `yaml_reference.md` and individual `config.md` files within the `src/dashboard_compiler/` subdirectories (see `quickstart.md` - Additional Resources).

---

## Onboarding Steps

- **Understand Core Architecture:** Review `architecture.md` to grasp the overall design and data flow.
- **Explore YAML Schema:** Read `yaml_reference.md` and `quickstart.md` for a comprehensive understanding of the YAML configuration structure and examples.
- **Examine Pydantic Models:** Dive into `src/dashboard_compiler/**/config.py` files to see the definitive source of truth for configuration options, types, and validation rules.
- **Trace Compilation Logic:** Follow the `compile_dashboard` function in `src/dashboard_compiler/dashboard/compile.py` to understand how YAML models are transformed into Kibana JSON view models.
- **Run Tests:** Execute `uv run pytest` and inspect the `tests/__snapshots__/` directory to see examples of generated Kibana JSON for various dashboard configurations.

---

## CI/CD

GitHub Actions workflows in `.github/workflows/`:

- **test.yml**: Runs tests, linting, and type checking
- **claude-on-mention.yml**: Claude Code assistant (can make PRs when @claude mentioned)
- **claude-on-open-label.yml**: Claude triage assistant (read-only analysis on labeled issues or newly opened unassigned issues)
- **claude-on-merge-conflict.yml**: Claude merge conflict resolver (automatically resolves merge conflicts in PRs)

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
