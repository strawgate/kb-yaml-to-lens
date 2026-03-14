"""MkDocs hook to generate llms.txt and llms-full.txt files during build."""

import logging
import re
from pathlib import Path
from typing import Any

import html2text
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

log = logging.getLogger('mkdocs.plugins.llms_txt')

# State to collect processed page content in navigation order
_collected_pages: dict[str, str] = {}
_nav_order: list[str] = []


def write_file(path: Path, content: str) -> None:
    """Write content to a file."""
    _ = path.write_text(data=content, encoding='utf-8')
    log.info(msg=f'Generated {path} ({len(content)} characters)')


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


def on_files(files: Files, config: MkDocsConfig) -> Files:
    """Generate llms.txt navigation file and add both txt files to the build.

    Note: llms-full.txt content is generated in on_post_build after all pages are processed.
    """
    global _nav_order  # noqa: PLW0603
    docs_dir = Path(config.docs_dir)

    # Extract navigation order for later use
    nav: list[Any] = config.nav or []  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    _nav_order = extract_files_from_nav(nav)  # pyright: ignore[reportUnknownArgumentType]
    _nav_order = list(dict.fromkeys(_nav_order))  # Deduplicate while preserving order

    log.info(f'Extracted {len(_nav_order)} files from navigation for llms-full.txt')

    # Generate llms.txt content (navigation file - static content)
    llms_txt_content: str = generate_llms_txt_content(config)
    llms_txt_path: Path = docs_dir / 'llms.txt'
    write_file(path=llms_txt_path, content=llms_txt_content)

    # Create empty llms-full.txt placeholder (will be populated in on_post_build)
    llms_full_path: Path = docs_dir / 'llms-full.txt'
    write_file(path=llms_full_path, content='# Placeholder - generated during build\n')

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


def on_page_content(html: str, page: Page, config: MkDocsConfig, files: Files) -> str:  # noqa: ARG001
    """Collect processed HTML content for each page after mkdocstrings expansion."""
    src_path = page.file.src_path
    _collected_pages[src_path] = html
    log.debug(f'Collected content for {src_path} ({len(html)} chars)')
    return html


def _convert_html_to_markdown(html_content: str) -> str:
    """Convert HTML to clean markdown suitable for LLMs."""
    h = html2text.HTML2Text()
    h.body_width = 0  # Don't wrap lines
    h.ignore_links = False
    h.ignore_images = True
    h.ignore_emphasis = False
    h.mark_code = True
    h.wrap_links = False
    h.wrap_list_items = False
    h.pad_tables = True  # Better table formatting
    h.default_image_alt = ''
    h.ignore_tables = False

    markdown = h.handle(html_content)

    # Clean up excessive whitespace
    markdown = re.sub(r'\n{4,}', '\n\n\n', markdown)

    # Remove anchor links like [¶](#section)
    markdown = re.sub(r'\[¶\]\([^)]*\)', '', markdown)

    # Clean up empty links
    markdown = re.sub(r'\[\]\([^)]*\)', '', markdown)

    return markdown.strip()


def on_post_build(config: MkDocsConfig) -> None:
    """Generate llms-full.txt with processed content after build completes."""
    docs_dir = Path(config.docs_dir)
    site_dir = Path(config.site_dir)

    output: list[str] = []

    # Add header
    output.append('# Dashboard Compiler - Complete Documentation\n\n')
    output.append('> This file contains all documentation for the Dashboard Compiler project.\n\n')
    output.append('---\n\n')

    # Concatenate pages in navigation order
    pages_included = 0
    for file_path in _nav_order:
        if file_path not in _collected_pages:
            log.warning(f'{file_path} not in collected pages, skipping...')
            continue

        html_content = _collected_pages[file_path]

        # Convert HTML to markdown
        markdown_content = _convert_html_to_markdown(html_content)

        # Add file separator and content
        output.append(f'\n\n---\n# Source: {file_path}\n---\n\n')
        output.append(markdown_content)
        pages_included += 1

    content = ''.join(output)

    # Write to docs dir (source)
    llms_full_path = docs_dir / 'llms-full.txt'
    write_file(path=llms_full_path, content=content)

    # Also write directly to site dir (built output)
    site_llms_full_path = site_dir / 'llms-full.txt'
    write_file(path=site_llms_full_path, content=content)

    log.info(f'Generated llms-full.txt with {pages_included} pages ({len(content)} characters)')

    # Clear state for potential subsequent builds (e.g., during serve)
    _collected_pages.clear()


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
