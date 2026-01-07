# Agent Guidelines: kb-yaml-to-lens Project

> Multi-language project for compiling Kibana dashboards from YAML to Lens format
> Python compiler · TypeScript VS Code extension · JavaScript fixture generator

---

## Project Overview

This repository contains three main components:

1. **Dashboard Compiler** - Core YAML → JSON compilation engine
2. **VS Code Extension** - Live preview and visual editing
3. **Fixture Generator** - Kibana API-based test fixture generation

### Repository Structure

| Directory | Technology | Purpose | AGENTS.md |
| --------- | ---------- | ------- | --------- |
| `src/dashboard_compiler/` | Python 3.12+ | Core compilation logic | `src/dashboard_compiler/AGENTS.md` |
| `vscode-extension/` | TypeScript/Node.js | VS Code extension | `vscode-extension/AGENTS.md` |
| `fixture-generator/` | JavaScript/Docker | Kibana fixture generation | `fixture-generator/AGENTS.md` |
| `tests/` | Python pytest | Unit tests for compiler | `src/dashboard_compiler/AGENTS.md` |
| `inputs/` | YAML | Example dashboards | - |
| `docs/` | Markdown | Documentation | - |

### Common Commands

Root-level commands orchestrate all components via `make`:

| Command | Purpose |
| --------- | --------- |
| `make install` | Install all dependencies (all components) |
| `make ci` or `make check` | **Run before committing** (all linting + typecheck + all tests) |
| `make fix` | Auto-fix all linting issues (all components) |
| `make lint-all-check` | Check all linting without fixing (all components) |
| `make test-all` | Run all tests (all components) |
| `make test` | Run Python unit tests only |
| `make typecheck` | Run type checking with basedpyright |
| `make compile` | Compile YAML dashboards to NDJSON |

**Component-specific Makefiles:**

- `vscode-extension/Makefile` - Extension development commands
- `fixture-generator/Makefile` - Fixture generation commands

Component-specific commands can be run by cd-ing into the component directory. See component-specific AGENTS.md files for available commands.

**Workflow example:**

```bash
# First time setup
make install

# Development cycle
# 1. Make changes
# 2. Auto-fix linting issues
make fix
# 3. Run all CI checks (linting + typecheck + tests)
make ci
```

---

## AI Agent Guidelines

**Read the docs first:**

- When working in any component, read the README.md or AGENTS.md/CLAUDE.md for the component you're working on.

**Read Before Modify:**

- Never speculate about code you haven't read
- Always inspect existing implementations before suggesting changes
- Search for similar patterns across the codebase

**Maintain Consistency:**

- Always search for existing patterns in the codebase to maintain consistency
- Follow existing code patterns within each component
- Match the style and conventions of surrounding code
- Don't introduce new patterns without strong justification

**Verify Your Work:**

- Run component-specific tests before committing
- Ensure all checks pass (lint, typecheck, tests)
- Test the actual functionality, not just that it compiles

**Be Honest:**

- Document unresolved items
- Acknowledge when you're uncertain
- Never claim work is complete with critical issues unresolved

**Be Thorough:**

- Go the extra mile!
- Update documentation and tests when you make code changes. These are not typically near the code so make sure you thoroughly search for items to update.
- Consider the broader impact of your changes.

**Slop-Free since 1993:**

- No slop, no excuses, no half-measures
- No slop comments, no slop code, no slop logic, no slop architecture, no slop design, no slop anything.
- Avoid comments that simply state what the code is obviously doing
- Do not write comments that contrast the current implementation with a previous implementation (i.e. "this now does X" or "this class now contains Y")

---

## Working with Code Review Feedback

### Triage First

| Priority | Examples |
| ---------- | ---------- |
| **Critical** | Security issues, data corruption, type safety violations, test failures |
| **Important** | Error handling, performance, missing tests, type annotations |
| **Optional** | Style preferences, minor refactors |

### Evaluate Against Codebase

- Search for similar patterns before accepting suggestions
- If a pattern exists across multiple files, it's likely intentional
- Preserve consistency over isolated best practices

### Verification Requirements

- [ ] All critical issues addressed
- [ ] All important issues addressed or deferred with rationale
- [ ] Component-specific checks pass (see component AGENTS.md)
- [ ] Manual testing completed where applicable

---

## CI/CD

### Automated Workflows

The repository uses GitHub Actions for:

- **Testing & Quality Checks** — Automated linting, type checking, tests on every push/PR
- **Documentation** — Automatic deployment of docs to GitHub Pages
- **Claude AI Assistants** — Automated code assistance, issue triage, merge conflict resolution
- **Build Automation** — Docker image building for fixture generators

Each workflow has self-contained instructions. Claude receives both the workflow prompt and relevant AGENTS.md files.

### Modifying Workflows

**Claude CANNOT modify workflow files** in `.github/workflows/` due to GitHub App permissions. When attempting to push changes to workflow files, GitHub rejects the push with:

```text
refusing to allow a GitHub App to create or update workflow `.github/workflows/*` without `workflows` permission
```

**To request workflow changes:**

Copilot is extremely dumb and needs to be spoon-fed the exact change you want made. Do not give co-pilot options, do not rely on its expertise, do not trust its output.

1. Make the exact workflow file you want in a `github/` folder. Do not attempt to modify existing workflow files.
2. In your PR, indicate that you need a maintainer or Copilot to move the file into `.github/` as a new workflow file or a replacement for an existing workflow file.

---

## Pull Request Standards

### Requirements

- No merge conflicts with main
- No unrelated changes or plan files
- All static checks pass (component-specific)
- Self-review completed
- The repository's Pull Request Template is located at `.github/pull_request_template.md` and should be the basis for your initial PR body

### Self Code Review Checklist

- [ ] Solves the stated problem, with specific reference to the body of the related issue
- [ ] Code is complete, well-written, and follows existing patterns in codebase
- [ ] Tests added/updated as needed
- [ ] Documentation is still accurate after the changes
- [ ] All checks pass (linting + typecheck + tests) - run `make ci` to verify all checks pass

### Code Rabbit will review your PR

Code Rabbit will review your PR and provide feedback on the changes you made. CodeRabbit sometimes makes mistakes, so you should carefully consider the feedback and address the feedback if necessary. CodeRabbit will follow the rules outlined in ./CODERABBIT.md, ./CODE_STYLE.md, and this file (./AGENTS.md).

---

## Additional Resources

| Resource | Location |
| ---------- | ---------- |
| Component AGENTS.md files | `src/dashboard_compiler/AGENTS.md`, `vscode-extension/AGENTS.md`, `fixture-generator/AGENTS.md` |
| Architecture details | `docs/architecture.md` |
| Getting started guide | `docs/index.md` (includes installation and first dashboard tutorial) |
| Contributing guide | `CONTRIBUTING.md` |
| CLI documentation | `docs/CLI.md` |
