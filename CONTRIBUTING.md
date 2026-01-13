# Contributing Guide

## Development Guidelines

See [CLAUDE.md](CLAUDE.md) for AI agent guidelines and [component-specific AGENTS.md files](CLAUDE.md#project-overview) for detailed development guidelines.

## Code Style

See component-specific AGENTS.md files for code style conventions:

- Python/Compiler: [compiler/AGENTS.md](compiler/AGENTS.md#code-conventions)
- TypeScript/VS Code Extension: [vscode-extension/AGENTS.md](vscode-extension/AGENTS.md#development-guidelines)

## Pull Request Requirements

@CLAUDE.md#pull-request-standards

**Additional PR Requirements:**

When creating a pull request:

1. **Use the PR template** - GitHub will automatically populate it when you create a PR
2. **For config/compilation changes** - Include:
   - Sample YAML that demonstrates the change
   - Expected compilation outcome
   - How to verify the changes work
3. **For chart type modifications** - Complete the fixture generation checklist
4. **Run all checks** before submitting: `make ci`
