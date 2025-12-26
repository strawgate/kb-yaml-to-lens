# Contributing Guide

## Code Style and Quality

### Python

This project uses [Ruff](https://github.com/astral-sh/ruff) for Python code formatting and linting, and [basedpyright](https://github.com/DetachHead/basedpyright) for type checking:

- Line length: 140 characters
- Python version: 3.12+
- Quote style: Single quotes for inline code, double quotes for docstrings

Run linting, formatting, and type checking:

```bash
# Run all linters and formatters
make lint

# Run type checking
make typecheck
# or directly:
uv run basedpyright

# Run individually:
uv run ruff check . --fix
uv run ruff format .
```

### Markdown

This project uses [markdownlint](https://github.com/DavidAnson/markdownlint) for markdown file linting:

- Line length: 80 characters (excluding code blocks and tables)
- Configuration: `.markdownlint.jsonc`

Run markdown linting:

```bash
markdownlint --fix -c .markdownlint.jsonc .
# or via make:
make lint-markdown
```

### Documentation

Documentation is built using [MkDocs](https://www.mkdocs.org/) with the Material theme.

Preview documentation locally:

```bash
make docs-serve
```

Build documentation:

```bash
make docs-build
```

Deploy to GitHub Pages:

```bash
make docs-deploy
```

## Additional Lens Capabilities

Lens has a lot of capabilities built-in to it. This project is not intended to cover every capability with a simple to use yaml interface -- instead we offer key capabilities via a simplified interface while allowing ultimate customization via custom json.

## Adding a new Lens Capability

The way we add capabilities in this project is by first creating new samples in the samples directory containing the feature we want to add.

Once the sample is added, we decide on a config for that feature. Each sample has a corresponding config in configs.

If the config requires new keys, we update yaml-reference.md at the root of the project to include the new sample.

Otherwise, we use the config and the sample in our tests to ensure that ultimately we are always generating exactly the same json that Kibana / Lens would generate. For each test, we record the "diff" as a snapshot which is the difference between the generated model and the original model from kibana.
