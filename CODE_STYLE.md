# Code Style Guide

Each component has its own CODE_STYLE.md with language-specific conventions:

- **Python (compiler):** [compiler/CODE_STYLE.md](compiler/CODE_STYLE.md)
- **TypeScript (vscode-extension):** [vscode-extension/CODE_STYLE.md](vscode-extension/CODE_STYLE.md)

See the component-specific CODE_STYLE.md files for the full list of rules!

Files outside of these projects are subject to markdown linting and yaml linting.

## Documentation

The files in `docs/` are built using MkDocs. See `docs/mkdocs.yml` for the build configuration and requirements.

Files in docs have strict markdown linting and undergo a link verification step during CI which will fail if any links in the docs are broken.
