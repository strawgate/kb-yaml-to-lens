# Agent Guidelines: Dashboard Compiler (Python)

> **Dashboard Compiler** converts human-readable YAML into Kibana dashboard JSON.
> Python 3.12+ · Pydantic · PyYAML · uv package manager

---

---

## Project Architecture

### Data Flow

```text
YAML File → PyYAML Parser → Config Models (Pydantic) → Compile Functions → View Models → Kibana JSON
```

### Directory Structure

| Directory | Purpose |
| --------- | ------- |
| `src/dashboard_compiler/` | Core compilation logic |
| `src/dashboard_compiler/dashboard/` | Top-level dashboard config and compilation |
| `src/dashboard_compiler/panels/` | Panel types (markdown, links, images, search, charts) |
| `src/dashboard_compiler/panels/charts/` | Lens/ESQL chart types (metric, pie, xy) |
| `src/dashboard_compiler/controls/` | Dashboard control groups |
| `src/dashboard_compiler/filters/` | Filter compilation |
| `src/dashboard_compiler/queries/` | KQL, Lucene, ESQL query support |
| `src/dashboard_compiler/shared/` | Base models and utilities |
| `tests/` | Unit tests with snapshot testing (inline snapshots via `inline-snapshot` library) |
| `inputs/` | Example YAML dashboards |

### Three-Layer Pattern

Each component follows this structure:

1. **`config.py`** — Pydantic models defining YAML schema (source of truth)
2. **`view.py`** — Pydantic models defining Kibana JSON output
3. **`compile.py`** — Functions transforming config → view models

### Test Standards

New features and bug fixes should have corresponding and comprehensive tests. Our tests should be useful, easy to maintain and understand, and have proper documentation.

- **Use and prefer inline snapshots** via `inline-snapshot` library. Prefer snapshots over many assertions

---

## Code Conventions

@../../CODE_STYLE.md

@../../CODERABBIT.md

### Quick Reference: Finding Patterns

Before implementing a feature, use these searches to learn from existing code:

| Task | Search Strategy |
| ---- | --------------- |
| **Adding a new panel type** | `grep -r "isinstance.*Panel" src/dashboard_compiler/panels/compile.py` |
| **Adding a new chart type** | Study `src/dashboard_compiler/panels/charts/` directory structure |
| **Adding Pydantic validation** | `grep -r "@model_validator" src/` and look for `mode='after'` usage |
| **Handling union types** | Search for `isinstance` chains with final error handlers |
| **Adding a new config option** | Find similar options in `config.py` files, check if defaults in `compile.py` |

**Remember:** The codebase is your best teacher. Search, read, then implement following existing patterns.

### Documentation Updates

When updating YAML configuration docs:

1. `config.py` files are the source of truth for all configuration options
2. Each component's markdown should include: overview, minimal example, complex example, full options table
3. Table columns: `YAML Key`, `Data Type`, `Description`, `Default`, `Required`
4. Defaults are typically "Kibana Default" (defined in `compile.py`, not config or view models)

---

## AI Agent Guidelines

### Before Making Changes

1. **Read relevant files first** — Never speculate about code you haven't inspected
2. **Search for existing patterns** — Check how similar components handle the same problem
3. **Understand the architecture** — Config models → compile functions → view models
4. **Follow code style guidelines** — See CODE_STYLE.md for detailed conventions

### When Working on Chart Types (panels/charts/)

When modifying or creating chart compiler code, you need accurate reference data for what Kibana expects. Use the fixture generator to get this reference data:

#### Option 1: Reference Existing Fixtures (Preferred)

1. Check if a fixture already exists in `fixture-generator/output/` for this chart type
2. Read the existing fixture to understand the expected Kibana JSON structure
3. Compare your compiler output against the fixture to ensure accuracy
4. If the existing fixture doesn't cover your use case, create a new one (see Option 2)

#### Option 2: Create New Fixtures (For New Chart Types)

1. Create a fixture generator script in `fixture-generator/examples/<chart-type>.js`
2. Run `cd fixture-generator && make build` (if Docker image doesn't exist)
3. Run `cd fixture-generator && make run-example EXAMPLE=<chart-type>.js`
4. Verify the output JSON exists in `fixture-generator/output/`
5. Compare your compiler output with the Kibana-generated fixture
6. Commit BOTH the generator script AND output files

#### Option 3: (Worst Option) Review the Kibana Codebase for schema examples

Use the github code search tool to find examples of JSON from the chart type in the Kibana codebase and use those as references.

**Why use fixtures:**

Fixtures are generated from real Kibana APIs using the official LensConfigBuilder. This ensures you're working with accurate reference data for what Kibana actually expects, not assumptions. It takes a couple of minutes and is much faster than creating references manually.

See `fixture-generator/AGENTS.md` for detailed instructions.

### Verification Requirements

Before claiming work is complete:

- [ ] **For schema changes:** Cross-reference with official documentation (Kibana repo, API docs, etc.)
- [ ] **For test changes:** Explain WHY test data changed, not just WHAT changed
- [ ] **For type errors:** Verify the fix compiles AND is semantically correct
- [ ] **For Boolean checks:** All conditional statements use explicit comparisons
- [ ] **For type checking:** Run `make typecheck` to verify type correctness
- [ ] Run `make check` after EACH fix, not just at the end
- [ ] Test that the compiled output is valid (not just that it compiles)

### Radical Honesty

- **Document unresolved items** — Explain why they weren't addressed
- **Acknowledge uncertainty** — Ask if unclear about patterns or requirements
- **Report problems** — Share issues encountered during implementation
- **Share reasoning** — Explain why you rejected or deferred feedback
- **Admit limitations** — Be clear if unable to verify fixes work correctly

**Never claim work is complete with unresolved critical or important issues.**

---

## CI/CD

### Pre-commit Requirements

CI will fail if:

- Ruff linting fails
- Markdown/YAML linting fails
- Tests fail
- Type checking fails (basedpyright recommended mode)
- Docstring coverage below 80%
- Merge conflicts are present

Run `make ci` (or `make check`) locally before pushing.

---

## Additional Resources

| Resource | Location |
| -------- | -------- |
| Architecture details | `docs/architecture.md` |
| Getting started guide | `docs/index.md` (includes installation and first dashboard tutorial) |
| Contributing guide | `CONTRIBUTING.md` |
| CLI documentation | `docs/CLI.md` |
