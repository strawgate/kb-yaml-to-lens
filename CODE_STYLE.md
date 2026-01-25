# Code Style Guide

Each component has its own CODE_STYLE.md with language-specific conventions:

- **Python (compiler):** [packages/kb-dashboard-compiler/CODE_STYLE.md](packages/kb-dashboard-compiler/CODE_STYLE.md)
- **TypeScript (vscode-extension):** [packages/vscode-extension/CODE_STYLE.md](packages/vscode-extension/CODE_STYLE.md)

See the component-specific CODE_STYLE.md files for the full list of rules!

Files outside of these projects are subject to markdown linting and yaml linting.

## Documentation

The files in `packages/kb-dashboard-docs/` are built using MkDocs. See `packages/kb-dashboard-docs/mkdocs.yml` for the build configuration and requirements.

Files in `packages/kb-dashboard-docs/` have strict markdown linting and undergo a link verification step during CI which will fail if any links in `packages/kb-dashboard-docs/` are broken.
