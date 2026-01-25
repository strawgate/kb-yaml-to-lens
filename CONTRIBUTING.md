# Contributing Guide

Thank you for contributing to kb-yaml-to-lens!

## Getting Started

See [DEVELOPING.md](DEVELOPING.md) for development setup and workflows.

## Code Style

See [CODE_STYLE.md](CODE_STYLE.md) for project-wide conventions, and component-specific guides:

- **Python:** [packages/kb-dashboard-compiler/CODE_STYLE.md](packages/kb-dashboard-compiler/CODE_STYLE.md)
- **TypeScript:** [packages/vscode-extension/CODE_STYLE.md](packages/vscode-extension/CODE_STYLE.md)

## Pull Request Process

### Before Submitting

1. **Run all checks:** `make all ci`
2. **Self-review your changes:**
   - Does it solve the stated problem?
   - Does the code follow existing patterns?
   - Are tests added/updated as needed?

### PR Requirements

- No merge conflicts with `main`
- All CI checks pass
- Use the [PR template](.github/pull_request_template.md)

### For Config/Compilation Changes

When modifying how YAML is parsed or compiled:

1. Include sample YAML that demonstrates the change
2. Describe the expected compilation outcome
3. Explain how to verify the changes work

### For Chart Type Modifications

Complete the fixture generation checklist in the PR template.

## Reporting Issues

Use GitHub Issues for:

- Bug reports (include reproduction steps)
- Feature requests (explain the use case)
- Documentation improvements

## Questions?

Open a GitHub Discussion for questions about usage or development.
