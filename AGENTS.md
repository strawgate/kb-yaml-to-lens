# Agent Guidelines: Dashboard Compiler

> **Dashboard Compiler** converts human-readable YAML into Kibana dashboard JSON.
> Python 3.12+ · Pydantic · PyYAML · uv package manager

---

## Quick Reference

### Essential Commands

| Command | Purpose |
|---------|---------|
| `make install` | Install all dependencies |
| `make check` | **Run before committing** (lint + test) |
| `make test` | Run pytest suite |
| `make lint` | Format and lint code |
| `make compile` | Compile YAML dashboards to NDJSON |

### Common Workflows

```bash
# First time setup
make install

# Development cycle
# 1. Make changes
# 2. Run checks
make check

# Test specific file
uv run pytest tests/panels/test_metrics.py
```

---

## Project Architecture

### Data Flow

```
YAML File → PyYAML Parser → Config Models (Pydantic) → Compile Functions → View Models → Kibana JSON
```

### Directory Structure

| Directory | Purpose |
|-----------|---------|
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

- **Use inline snapshots** via `inline-snapshot` library (not external snapshot files)
- **Avoid scenario-based tests** in separate JSON files
- **Write pytest tests directly** in Python
- See existing tests for patterns (e.g., `tests/panels/charts/lens/metrics/test_metrics.py`)

---

## Code Conventions

### Style

- **Line length**: 140 characters (Ruff enforced)
- **Dependency manager**: `uv` (not Poetry)
- **Docstring coverage**: 80% threshold

### Pydantic Models

**Configuration Models** (`BaseCfgModel`):

- Settings: `strict=True`, `extra='forbid'`, `frozen=True`, `validate_default=True`
- Use attribute docstrings for field descriptions
- Location: `**/config.py` files

**View Models** (`BaseVwModel`):

- Custom serializer omits fields with `OmitIfNone` metadata when value is `None`
- May narrow types in subclasses (e.g., `str` → `Literal['value']`)
- `reportIncompatibleVariableOverride = false` in basedpyright allows this

### Documentation Updates

When updating YAML configuration docs:

1. `config.py` files are the source of truth for all configuration options
2. Each component's markdown should include: overview, minimal example, complex example, full options table
3. Table columns: `YAML Key`, `Data Type`, `Description`, `Default`, `Required`
4. Defaults are typically "Kibana Default" (defined in `compile.py`, not config models)
5. Run `uv run python scripts/compile_docs.py` to regenerate `yaml_reference.md`

---

## AI Agent Guidelines

### Before Making Changes

1. **Read relevant files first** — Never speculate about code you haven't inspected
2. **Search for existing patterns** — Check how similar components handle the same problem
3. **Understand the architecture** — Config models → compile functions → view models

### Working with Code Review Feedback

#### Triage First

| Priority | Examples |
|----------|----------|
| **Critical** | Security issues, data corruption, type safety violations, test failures |
| **Important** | Error handling, performance, missing tests, type annotations |
| **Optional** | Style preferences, minor refactors |

#### Evaluate Against Codebase

- Search for similar patterns before accepting suggestions
- If a pattern exists across multiple panels/charts, it's likely intentional
- Preserve consistency over isolated best practices

#### Verification Requirements

Before claiming feedback is addressed:

- [ ] **For schema changes:** Cross-reference with official documentation (Kibana repo, API docs, etc.)
- [ ] **For test changes:** Explain WHY test data changed, not just WHAT changed
- [ ] **For type errors:** Verify the fix compiles AND is semantically correct
- [ ] Run `make check` after EACH fix, not just at the end
- [ ] Test that the compiled output is valid (not just that it compiles)

#### Before Claiming Complete

- [ ] All critical issues addressed or documented as out-of-scope
- [ ] All important issues addressed or explicitly deferred with rationale
- [ ] `make check` passes
- [ ] Type checking passes (basedpyright in CI)
- [ ] Tests pass with updated snapshots if needed

#### Documenting Deferrals

If feedback isn't implemented, explain why:

- Conflicts with established pattern (cite similar code)
- Out of scope for component purpose
- Trade-off not worth the complexity

### Radical Honesty

- **Document unresolved items** — Explain why they weren't addressed
- **Acknowledge uncertainty** — Ask if unclear about patterns or requirements
- **Report problems** — Share issues encountered during implementation
- **Share reasoning** — Explain why you rejected or deferred feedback
- **Admit limitations** — Be clear if unable to verify fixes work correctly

**Never claim work is complete with unresolved critical or important issues.**

### Resolving PR Review Threads

You can resolve review threads via GitHub GraphQL API. **Only resolve after making code changes that address the feedback.**

```bash
# Get review threads
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      pullRequest(number: PR_NUMBER) {
        reviewThreads(first: 100) {
          nodes { id isResolved path line
            comments(first: 10) { nodes { body author { login } } }
          }
        }
      }
    }
  }' -f owner=OWNER -f name=REPO -F number=PR_NUMBER

# Resolve a thread (after fixing the issue)
gh api graphql -f query='
  mutation {
    resolveReviewThread(input: {threadId: "THREAD_ID"}) {
      thread { id isResolved }
    }
  }'
```

**Note**: Claude will NOT add comments or reviews to PRs. It can only resolve threads after making code changes.

---

## CI/CD

### Automated Workflows

The repository uses GitHub Actions for:

- **Testing & Quality Checks** — Automated linting, type checking, tests on every push/PR
- **Documentation** — Automatic deployment of docs to GitHub Pages
- **Claude AI Assistants** — Automated code assistance, issue triage, merge conflict resolution, and project management
- **Build Automation** — Docker image building for fixture generators

Each workflow has self-contained instructions. Claude receives both the workflow prompt and this AGENTS.md file.

### GitHub Actions Workflow Patterns

When creating new Claude-powered workflows:

1. **Use the shared workflow:** `.github/workflows/run-claude.yml`
2. **Standard MCP configuration** (automatically set up in shared workflow):
   - `repository-summary` - For generating AGENTS.md summaries
   - `code-search` - For searching code across repo
   - `github-research` - For issue/PR analysis
3. **Don't manually configure MCP servers** - use the shared workflow's built-in setup

**Example:**

```yaml
jobs:
  my-claude-job:
    uses: ./.github/workflows/run-claude.yml
    with:
      checkout-ref: ${{ github.event.pull_request.head.ref }}
      prompt: |
        Your task here...
      allowed-tools: mcp__github-research,Bash
    secrets:
      claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

**Note:** The `repository-summary` tool (formerly `agents_md_generator`) is automatically available but rarely needed.

### Pre-commit Requirements

CI will fail if:

- Ruff linting fails
- Tests fail
- Type checking fails (basedpyright standard mode)
- Docstring coverage below 80%

Run `make check` locally before pushing.

---

## Pull Request Standards

### Requirements

- No merge conflicts with main
- No unrelated changes or plan files
- All static checks pass
- Self-review completed

### Self Code Review Checklist

- [ ] Solves the stated problem
- [ ] Code is complete and well-written
- [ ] Follows existing patterns in codebase
- [ ] Tests added/updated as needed
- [ ] Documentation updated if API changed

---

## Additional Resources

| Resource | Location |
|----------|----------|
| Architecture details | `docs/architecture.md` |
| YAML schema reference | `yaml_reference.md` |
| Quickstart guide | `docs/quickstart.md` |
| Contributing guide | `CONTRIBUTING.md` |
| CLI documentation | `docs/CLI.md` |
