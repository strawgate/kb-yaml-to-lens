# Contributing Guide

Thank you for contributing to kb-yaml-to-lens!

## Getting Started

See [DEVELOPING.md](DEVELOPING.md) for development setup and workflows.

## Code Style

See [CODE_STYLE.md](CODE_STYLE.md) for project-wide conventions, and component-specific guides:

- **Python (CLI):** [packages/kb-dashboard-cli/CODE_STYLE.md](packages/kb-dashboard-cli/CODE_STYLE.md)
- **Python (Core):** [packages/kb-dashboard-core/CODE_STYLE.md](packages/kb-dashboard-core/CODE_STYLE.md)
- **TypeScript:** [packages/vscode-extension/CODE_STYLE.md](packages/vscode-extension/CODE_STYLE.md)

## Pull Request Process

### Before Submitting/Updating

1. **Check for merge conflicts:** `make check-merge-conflicts`
   - This checks if merging your branch with `main` would cause conflicts
   - Resolve any conflicts before submitting your PR
2. **Run all checks:** `make all ci`
3. **Self-review your changes:**
   - Does it solve the stated problem?
   - Does the code follow existing patterns?
   - Are tests added/updated as needed?
4. **Check for recent comments/feedback:**
   - Check to make sure no new feedback or comments have been added since you started working on your updates.
5. **Follow the PR template:**
   - Fill out the [PR template](.github/pull_request_template.md) with the necessary information.
6. **One Last Check:**
   - Review the relevant [Code Style](CODE_STYLE.md) and [Contributing Guide](CONTRIBUTING.md) documents to make sure your changes follow the project's conventions.

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
