"""MkDocs hook to generate llms.txt and llms-full.txt files during build."""

import logging
from pathlib import Path
from typing import Any

from mkdocs.config.defaults import MkDocsConfig

log = logging.getLogger('mkdocs.plugins.llms_txt')


def on_post_build(config: MkDocsConfig, **_kwargs: Any) -> None:
    """Generate llms.txt files after the build completes."""
    site_dir = Path(config['site_dir'])

    # Generate llms.txt (navigation file)
    generate_llms_txt(site_dir, config)

    # Generate llms-full.txt (full content file)
    generate_llms_full_txt(site_dir, config)

    log.info('Generated llms.txt and llms-full.txt')


def generate_llms_txt(site_dir: Path, config: dict[str, Any]) -> None:
    """Generate the llms.txt navigation file."""
    site_url = config.get('site_url', '').rstrip('/')

    content = f"""# Dashboard Compiler

> Convert human-friendly YAML dashboard definitions into Kibana NDJSON format. Python compiler,
> TypeScript VS Code extension, and JavaScript fixture generator for creating and managing Kibana
> dashboards.

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

    output_path = site_dir / 'llms.txt'
    try:
        output_path.write_text(content, encoding='utf-8')
        log.info(f'Generated {output_path} ({len(content)} characters)')
    except OSError:
        log.exception(f'Failed to write {output_path}')
        raise


def extract_files_from_nav(nav_item: str | dict[str, Any] | list[Any], files: list[str] | None = None) -> list[str]:
    """Recursively extract file paths from MkDocs navigation structure."""
    if files is None:
        files = []

    if isinstance(nav_item, str):
        files.append(nav_item)
    elif isinstance(nav_item, dict):
        for value in nav_item.values():
            extract_files_from_nav(value, files)
    elif isinstance(nav_item, list):
        for item in nav_item:
            extract_files_from_nav(item, files)

    return files


def generate_llms_full_txt(site_dir: Path, config: dict[str, Any]) -> None:
    """Generate the llms-full.txt file with complete documentation content."""
    docs_dir = Path(config.get('docs_dir', 'docs'))

    # Extract files from navigation structure
    nav = config.get('nav', [])

    # Extract all files from navigation (all sections)
    all_files = extract_files_from_nav(nav)
    # Deduplicate while preserving order
    all_files = list(dict.fromkeys(all_files))

    log.info(f'Extracted {len(all_files)} files from navigation')

    output = []

    # Add header
    output.append('# Dashboard Compiler - Complete Documentation\n\n')
    output.append('> This file contains all documentation for the Dashboard Compiler project.\n\n')
    output.append('---\n\n')

    # Concatenate all files
    for file_path in all_files:
        path = docs_dir / file_path
        try:
            content = path.read_text(encoding='utf-8')
        except FileNotFoundError:
            log.warning(f'{file_path} not found, skipping...')
            continue
        except OSError as e:
            log.warning(f'Failed to read {file_path}: {e}, skipping...')
            continue

        # Add file separator
        output.append(f'\n\n---\n# Source: {file_path}\n---\n\n')
        output.append(content)

    # Write output
    output_path = site_dir / 'llms-full.txt'
    full_content = ''.join(output)
    try:
        output_path.write_text(full_content, encoding='utf-8')
        log.info(f'Generated {output_path} ({len(full_content)} characters)')
    except OSError:
        log.exception(f'Failed to write {output_path}')
        raise
