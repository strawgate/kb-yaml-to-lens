"""MkDocs hook to generate llms.txt and llms-full.txt files during build."""

import logging
from pathlib import Path

log = logging.getLogger("mkdocs.plugins.llms_txt")


def on_post_build(config, **kwargs):
    """Generate llms.txt files after the build completes."""
    site_dir = Path(config["site_dir"])

    # Generate llms.txt (navigation file)
    generate_llms_txt(site_dir, config)

    # Generate llms-full.txt (full content file)
    generate_llms_full_txt(site_dir, config)

    log.info("Generated llms.txt and llms-full.txt")


def generate_llms_txt(site_dir: Path, config: dict) -> None:
    """Generate the llms.txt navigation file."""
    site_url = config.get("site_url", "").rstrip("/")

    content = f"""# Dashboard Compiler

> Convert human-friendly YAML dashboard definitions into Kibana NDJSON format. Python compiler, TypeScript VS Code extension, and JavaScript fixture generator for creating and managing Kibana dashboards.

## Getting Started

- [Installation and Quick Start]({site_url}/): Get up and running with your first dashboard
- [CLI Reference]({site_url}/CLI/): Complete command-line documentation
- [VS Code Extension]({site_url}/vscode-extension/): Live preview and visual editing

## User Guide

- [Dashboard Configuration]({site_url}/dashboard/dashboard/): Dashboard-level settings and options
- [Panel Types Overview]({site_url}/panels/base/): Common configuration for all panel types
- [Lens Panels]({site_url}/panels/lens/): Chart panels (metric, pie, XY, gauge, datatable, etc.)
- [Dashboard Controls]({site_url}/controls/config/): Interactive filtering controls
- [Filters and Queries]({site_url}/filters/config/): Data filtering and query configuration
- [Complete Examples]({site_url}/examples/): Real-world YAML dashboard examples

## Developer Guide

- [Programmatic Usage]({site_url}/programmatic-usage/): Python API for dynamic dashboard generation
- [Architecture Overview]({site_url}/architecture/): Technical design and data flow
- [API Reference]({site_url}/api/): Auto-generated Python API documentation

## Optional

- [Kibana Architecture Reference]({site_url}/kibana-architecture/): Understanding Kibana's internal structure
- [Fixture Generator Guide]({site_url}/kibana-fixture-generator-guide/): Generating test fixtures from live Kibana
- [PyPI Publishing]({site_url}/pypi-publishing/): Package release process
"""

    output_path = site_dir / "llms.txt"
    output_path.write_text(content)
    log.info(f"Generated {output_path} ({len(content)} characters)")


def generate_llms_full_txt(site_dir: Path, config: dict) -> None:
    """Generate the llms-full.txt file with complete user guide content."""
    docs_dir = Path(config.get("docs_dir", "docs"))

    # User guide files in order of importance
    user_guide_files = [
        "index.md",
        "CLI.md",
        "vscode-extension.md",
        "dashboard/dashboard.md",
        "panels/base.md",
        "panels/lens.md",
        "panels/metric.md",
        "panels/pie.md",
        "panels/xy.md",
        "panels/gauge.md",
        "panels/datatable.md",
        "panels/markdown.md",
        "panels/links.md",
        "panels/image.md",
        "panels/search.md",
        "panels/tagcloud.md",
        "panels/esql.md",
        "controls/config.md",
        "filters/config.md",
        "queries/config.md",
        "advanced/color-assignments.md",
        "advanced/esql-views.md",
        "examples/index.md",
    ]

    output = []

    # Add header
    output.append("# Dashboard Compiler - Complete User Guide\n\n")
    output.append("> This file contains all user guide documentation for the Dashboard Compiler project.\n\n")
    output.append("---\n\n")

    # Concatenate all files
    for file_path in user_guide_files:
        path = docs_dir / file_path
        if not path.exists():
            log.warning(f"{file_path} not found, skipping...")
            continue

        content = path.read_text()

        # Add file separator
        output.append(f"\n\n---\n# Source: {file_path}\n---\n\n")
        output.append(content)

    # Write output
    output_path = site_dir / "llms-full.txt"
    full_content = "".join(output)
    output_path.write_text(full_content)
    log.info(f"Generated {output_path} ({len(full_content)} characters)")
