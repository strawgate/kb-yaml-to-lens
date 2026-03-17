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

1. **Check for merge conflicts:** `just check-merge-conflicts`
   - This checks if merging your branch with `main` would cause conflicts
   - Resolve any conflicts before submitting your PR
2. **Run all checks:** `just all ci`
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

When modifying how YAML is parsed or compiled, PRs **MUST** meet all of the
following requirements. PRs that do not meet these requirements will be sent back
for revision.

1. **YAML samples MUST compile successfully.** Every sample YAML included in the
   PR must compile without errors against the current schema. Run
   `uv run kb-dashboard compile --input-file <file>` and confirm it succeeds before submitting. Never
   submit YAML that has not been verified to compile.
2. **Include both sample YAML AND verification instructions.** The PR must
   contain a complete, self-contained YAML configuration that exercises the
   change, along with detailed step-by-step instructions for reviewers to verify
   the behavior.
3. **Verification instructions must include exact commands and expected
   outcomes.** Provide the specific bash commands a reviewer should run (e.g.,
   `uv run kb-dashboard compile --input-file examples/my-change.yaml`) and describe what the compiled
   output should contain or how the resulting dashboard should behave in Kibana.
4. **Describe the expected compilation outcome.** Explain what the compiled
   NDJSON should look like, what Kibana UI elements should reflect, or what
   behavioral differences the change introduces.

See [PR #1220](https://github.com/strawgate/kb-yaml-to-lens/pull/1220) for an
example of a well-structured config/compilation PR that includes a test sample
config, expected outcome, and verification commands.

### For Chart Type Modifications

Complete the fixture generation checklist in the PR template.

## Reporting Issues

Use GitHub Issues for:

- Bug reports (include reproduction steps)
- Feature requests (explain the use case)
- Documentation improvements

## Questions?

Open a GitHub Discussion for questions about usage or development.
