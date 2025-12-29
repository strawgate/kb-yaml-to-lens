# Agent Guidelines: kb-yaml-to-lens Project

> Multi-language project for compiling Kibana dashboards from YAML to Lens format
> Python compiler · TypeScript VS Code extension · JavaScript fixture generator

---

## Project Overview

This repository contains three main components:

1. **Dashboard Compiler** (Python) - Core YAML → JSON compilation engine
2. **VS Code Extension** (TypeScript) - Live preview and visual editing
3. **Fixture Generator** (JavaScript/Docker) - Kibana API-based test fixture generation

**Important:** Each component has its own `AGENTS.md` file with component-specific guidelines. When working on a specific component, refer to the relevant AGENTS.md:

- Python compiler: `src/dashboard_compiler/AGENTS.md`
- VS Code extension: `vscode-extension/AGENTS.md`
- Fixture generator: `fixture-generator/AGENTS.md`

---

## Quick Reference

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

**From repository root:**

| Command | Purpose |
| --------- | --------- |
| `make install` | Install all dependencies |
| `make check` | **Run before committing** (lint + typecheck + test) |
| `make test` | Run pytest suite |
| `make lint` | Format and lint code |
| `make typecheck` | Run type checking with basedpyright |
| `make compile` | Compile YAML dashboards to NDJSON |

**Component-specific commands:**

See component-specific AGENTS.md files for detailed commands.

**Workflow example:**

```bash
# First time setup
make install

# Development cycle
# 1. Make changes
# 2. Run checks
make check
```

---

## AI Agent Guidelines

### Before Starting Work

1. **Identify the component** you're working on (Python compiler, VS Code extension, fixture generator)
2. **Read the component-specific AGENTS.md** for detailed guidelines
3. **Read relevant files** before making changes
4. **Search for patterns** in the codebase to maintain consistency

### General Principles

**Read Before Modify:**

- Never speculate about code you haven't read
- Always inspect existing implementations before suggesting changes
- Search for similar patterns across the codebase

**Maintain Consistency:**

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

### Modifying Workflows

**Claude CANNOT modify workflow files** in `.github/workflows/` due to GitHub App permissions. When attempting to push changes to workflow files, GitHub rejects the push with:

```text
refusing to allow a GitHub App to create or update workflow `.github/workflows/*` without `workflows` permission
```

**To request workflow changes:**

1. **Use @copilot** - Copilot (copilot-swe-agent[bot]) has full filesystem access and can modify workflows
2. **Provide exact specifications** - Since Copilot requires very specific instructions, provide:
   - Exact file path (e.g., `.github/workflows/claude-on-mention.yml`)
   - Exact line numbers or context to modify
   - Exact text to add/change/remove
   - Clear explanation of the desired behavior

**Example request to Copilot:**

```text
@copilot please update .github/workflows/claude-on-mention.yml
line 50: change allowed-tools to include Read,Write,Edit tools
```

**Workflow modification capabilities by agent:**

- **Claude** - ❌ Cannot push workflow changes (GitHub App limitation)
- **Copilot** - ✅ Can create/modify workflows directly
- **CodeRabbit** - ❌ Review-only, cannot make commits

---

## Resolving PR Review Threads

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

## Pull Request Standards

### Requirements

- No merge conflicts with main
- No unrelated changes or plan files
- All static checks pass (component-specific)
- Self-review completed

### Self Code Review Checklist

- [ ] Solves the stated problem
- [ ] Code is complete and well-written
- [ ] Follows existing patterns in codebase
- [ ] Tests added/updated as needed
- [ ] Documentation updated if API changed
- [ ] Component-specific checks pass

---

## Additional Resources

| Resource | Location |
| ---------- | ---------- |
| Component AGENTS.md files | `src/dashboard_compiler/AGENTS.md`, `vscode-extension/AGENTS.md`, `fixture-generator/AGENTS.md` |
| Architecture details | `docs/architecture.md` |
| YAML schema reference | `docs/yaml_reference.md` (generated via `make compile-docs`) |
| Quickstart guide | `docs/quickstart.md` |
| Contributing guide | `CONTRIBUTING.md` |
| CLI documentation | `docs/CLI.md` |
