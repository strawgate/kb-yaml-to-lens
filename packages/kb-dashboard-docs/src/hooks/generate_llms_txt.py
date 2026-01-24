"""MkDocs hook to generate llms.txt and llms-full.txt files during build."""

import logging
from pathlib import Path
from typing import Any

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files

log = logging.getLogger('mkdocs.plugins.llms_txt')

def write_file(path: Path, content: str) -> None:
    """Write content to a file."""
    _ = path.write_text(data=content, encoding='utf-8')
    log.info(msg=f'Generated {path} ({len(content)} characters)')

def on_files(files: Files, config: MkDocsConfig) -> Files:
    """Generate llms.txt files and add them to the build before link validation."""
    docs_dir = Path(config.docs_dir)

    # Generate llms.txt content
    llms_txt_content: str = generate_llms_txt_content(config)
    llms_txt_path: Path = docs_dir / 'llms.txt'
    write_file(path=llms_txt_path, content=llms_txt_content)

    # Generate llms-full.txt content
    llms_full_content: str = generate_llms_full_txt_content(config)
    llms_full_path: Path = docs_dir / 'llms-full.txt'
    write_file(path=llms_full_path, content=llms_full_content)

    # Add files to MkDocs file collection so they're included in the build
    # Remove existing files first to avoid deprecation warning
    for existing_file in list(files):
        if existing_file.src_path in ('llms.txt', 'llms-full.txt'):
            files.remove(existing_file)

    files.append(
        File(
            path='llms.txt',
            src_dir=str(docs_dir),
            dest_dir=config.site_dir,
            use_directory_urls=config.use_directory_urls,
        )
    )
    files.append(
        File(
            path='llms-full.txt',
            src_dir=str(docs_dir),
            dest_dir=config.site_dir,
            use_directory_urls=config.use_directory_urls,
        )
    )

    log.info('Added llms.txt and llms-full.txt to build files')
    return files


def generate_llms_txt_content(config: MkDocsConfig) -> str:
    """Generate the llms.txt navigation file content."""
    if config.site_url is None:
        msg = 'site_url is required'
        raise ValueError(msg)

    site_url: str = config.site_url.rstrip('/')

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
        for value in nav_item.values():  # pyright: ignore[reportAny]
            _ = extract_files_from_nav(value, files)  # pyright: ignore[reportAny]
    elif isinstance(nav_item, list):  # pyright: ignore[reportUnnecessaryIsInstance]
        for item in nav_item:  # pyright: ignore[reportAny]
            _ = extract_files_from_nav(item, files)  # pyright: ignore[reportAny]

    return files


def generate_llms_full_txt_content(config: MkDocsConfig) -> str:
    """Generate the llms-full.txt file content with complete documentation."""
    docs_dir: Path = Path(config.docs_dir)

    # Extract files from navigation structure
    nav: list[Any] = config.nav or []  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    # Extract all files from navigation (all sections)
    all_files = extract_files_from_nav(nav)  # pyright: ignore[reportUnknownArgumentType]
    # Deduplicate while preserving order
    all_files = list(dict.fromkeys(all_files))

    log.info(f'Extracted {len(all_files)} files from navigation')

    output: list[str] = []

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
