"""MkDocs hook to generate llms.txt and llms-full.txt files during build."""

import logging
from pathlib import Path
from typing import Any

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files

log = logging.getLogger('mkdocs.plugins.llms_txt')


def on_files(files: Files, config: MkDocsConfig, **_kwargs: Any) -> Files:
    """Generate llms.txt files and add them to the build before link validation."""
    docs_dir = Path(config['docs_dir'])

    # Generate llms.txt content
    llms_txt_content = generate_llms_txt_content(config)
    llms_txt_path = docs_dir / 'llms.txt'
    llms_txt_path.write_text(llms_txt_content, encoding='utf-8')
    log.info(f'Generated {llms_txt_path} ({len(llms_txt_content)} characters)')

    # Generate llms-full.txt content
    llms_full_content = generate_llms_full_txt_content(config)
    llms_full_path = docs_dir / 'llms-full.txt'
    llms_full_path.write_text(llms_full_content, encoding='utf-8')
    log.info(f'Generated {llms_full_path} ({len(llms_full_content)} characters)')

    # Add files to MkDocs file collection so they're included in the build
    files.append(
        File(
            path='llms.txt',
            src_dir=str(docs_dir),
            dest_dir=config['site_dir'],
            use_directory_urls=config['use_directory_urls'],
        )
    )
    files.append(
        File(
            path='llms-full.txt',
            src_dir=str(docs_dir),
            dest_dir=config['site_dir'],
            use_directory_urls=config['use_directory_urls'],
        )
    )

    log.info('Added llms.txt and llms-full.txt to build files')
    return files


def generate_llms_txt_content(config: dict[str, Any]) -> str:
    """Generate the llms.txt navigation file content."""
    site_url = config.get('site_url', '').rstrip('/')

    return f"""# Dashboard Compiler

> Convert human-friendly YAML dashboard definitions into Kibana NDJSON format. Python compiler
> and TypeScript VS Code extension for creating and managing Kibana dashboards.

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

## LLM-Driven Workflows

- [LLM Workflows Overview]({site_url}/llm-workflows/): Complete guide for using LLMs with kb-yaml-to-lens
- [Dashboard Decompiling Guide]({site_url}/dashboard-decompiling-guide/): Convert Kibana JSON to YAML
- [Dashboard Style Guide]({site_url}/dashboard-style-guide/): Best practices for dashboard design
- [llms-full.txt]({site_url}/llms-full.txt): Complete documentation for LLM context

## Developer Guide

- [Programmatic Usage]({site_url}/programmatic-usage/): Python API for dynamic dashboard generation
- [Architecture Overview]({site_url}/architecture/): Technical design and data flow
- [API Reference]({site_url}/api/): Auto-generated Python API documentation

## Optional

- [Kibana Architecture Reference]({site_url}/kibana-architecture/): Understanding Kibana's internal structure
- [PyPI Publishing]({site_url}/pypi-publishing/): Package release process
"""


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


def generate_llms_full_txt_content(config: dict[str, Any]) -> str:
    """Generate the llms-full.txt file content with complete documentation."""
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

    return ''.join(output)
