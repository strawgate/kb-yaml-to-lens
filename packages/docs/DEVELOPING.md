# Developing Documentation

Documentation is built with **MkDocs** using the Material theme.

## Structure

```text
docs/
├── index.md                 # Home page
├── api/                     # API reference (auto-generated from Python)
├── panels/                  # Panel type docs
├── examples/                # Example YAML files
└── hooks/                   # MkDocs build hooks (Python)
```

Navigation is defined in `mkdocs.yml`.

## Commands

Run from the `docs/` directory, or use pass-through from the repository root:

```bash
# Serve locally
cd docs && mkdocs serve

# Build
cd docs && mkdocs build

# Full check (lint + link verification)
make check-docs
```

**From repository root:** Use `make docs <target>` (e.g., `make docs test-links`).

## Adding Pages

1. Create markdown file in appropriate folder
2. Add to `nav:` in `mkdocs.yml`
3. Use relative links: `[text](../path/file.md)`

## Examples

All YAML examples should compile:

```bash
kb-dashboard compile --input-file docs/content/examples/your-file.yaml
```

See existing files in `examples/` for patterns.

## Link Verification

CI verifies all internal and external links. Run `make check-docs` before committing.

## Build Hooks

Python hooks in `hooks/` run during build (e.g., generating llms.txt). Test with `mkdocs build` from the `docs/` directory.
