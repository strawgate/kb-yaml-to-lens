"""MkDocs hook to generate llms.txt and llms-full.txt files during build."""

import importlib
import inspect
import logging
import re
from pathlib import Path
from typing import Any

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files

log = logging.getLogger('mkdocs.plugins.llms_txt')

# State to collect navigation order
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


_DIRECTIVE_BLOCK_RE = re.compile(r'(?ms)^:::\s+([A-Za-z_][\w\.-]*)\s*\n((?:^[ ]{4}.*\n?)*)')
_LLMS_EXCLUDE_BLOCK_RE = re.compile(r'(?ms)<!--\s*llms:exclude:start\s*-->[\s\S]*?<!--\s*llms:exclude:end\s*-->\n?')
_LLMS_EXCLUDE_INLINE_RE = re.compile(r'(?m)^.*<!--\s*llms:exclude\s*-->.*(?:\n|$)')
_POEM_SECTION_RE = re.compile(r'(?ms)^##\s+A Poem[^\n]*\n[\s\S]*?(?=^\s*---\s*$|\Z)')


def _format_annotation(annotation: Any) -> str:
    """Format type annotation for concise markdown output."""
    if annotation is inspect.Parameter.empty:
        return 'Any'
    return str(annotation).replace('typing.', '').replace('types.', '')


def _resolve_python_object(fully_qualified_name: str) -> Any | None:
    """Resolve object path like package.module.Class.attr to a Python object."""
    parts = fully_qualified_name.split('.')
    for idx in range(len(parts), 0, -1):
        module_name = '.'.join(parts[:idx])
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue

        obj: Any = module
        try:
            for attr in parts[idx:]:
                obj = getattr(obj, attr)
        except (AttributeError, TypeError):
            return None
        else:
            return obj
    return None


def _render_reference_block(fully_qualified_name: str) -> str | None:
    """Render selected mkdocstrings references into compact markdown.

    We only expand in-project references so we can filter and keep output focused.
    """
    if not fully_qualified_name.startswith('kb_dashboard_'):
        return None

    obj = _resolve_python_object(fully_qualified_name)
    if obj is None:
        return None

    lines: list[str] = [f'**{fully_qualified_name}**', '']

    doc = inspect.getdoc(obj)
    if doc:
        lines.extend([doc, ''])

    if inspect.isclass(obj):
        model_fields = getattr(obj, 'model_fields', None)
        if isinstance(model_fields, dict) and model_fields:
            lines.append('Fields:')
            for field_name, field in model_fields.items():
                annotation = _format_annotation(getattr(field, 'annotation', inspect.Parameter.empty))
                description = getattr(field, 'description', None) or ''
                suffix = f': {description}' if description else ''
                lines.append(f'- `{field_name}` (`{annotation}`){suffix}')
            lines.append('')
    elif inspect.isfunction(obj) or inspect.ismethod(obj):
        signature = str(inspect.signature(obj))
        lines.append(f'Signature: `{obj.__name__}{signature}`')
        lines.append('')

    return '\n'.join(lines).strip()


def _expand_mkdocstrings_references(markdown: str) -> str:
    """Post-process markdown and selectively inline mkdocstrings `:::` blocks."""

    def _replace(match: re.Match[str]) -> str:
        fully_qualified_name = match.group(1)
        # Keep llms-full focused on compiler APIs; CLI mkdocs-click refs are noisy here.
        if fully_qualified_name.startswith('mkdocs-click'):
            return ''
        rendered = _render_reference_block(fully_qualified_name)
        if rendered is None:
            return match.group(0)
        return f'{rendered}\n'

    return _DIRECTIVE_BLOCK_RE.sub(_replace, markdown)


def _strip_llms_excluded_blocks(markdown: str) -> str:
    """Remove explicit llms exclusion blocks/comments from markdown."""
    result = _LLMS_EXCLUDE_BLOCK_RE.sub('', markdown)
    return _LLMS_EXCLUDE_INLINE_RE.sub('', result)


def _strip_known_low_value_sections(markdown: str) -> str:
    """Remove sections that are useful for humans but noisy for llms-full."""
    return _POEM_SECTION_RE.sub('', markdown)


def on_post_build(config: MkDocsConfig) -> None:
    """Generate llms-full.txt by post-processing markdown sources.

    This is option 3 from issue #1234: selectively resolve mkdocstrings references
    in a second pass instead of relying on full HTML conversion.
    """
    docs_dir = Path(config.docs_dir)
    site_dir = Path(config.site_dir)

    try:
        output: list[str] = []

        # Add header
        output.append('# Dashboard Compiler - Complete Documentation\n\n')
        output.append('> This file contains all documentation for the Dashboard Compiler project.\n\n')
        output.append('---\n\n')

        # Concatenate pages in navigation order
        pages_included = 0
        included_paths: set[str] = set()
        for file_path in _nav_order:
            source_file = docs_dir / file_path
            if not source_file.exists():
                log.warning(f'{file_path} not found in docs dir, skipping...')
                continue

            markdown_content = source_file.read_text(encoding='utf-8')
            markdown_content = _strip_llms_excluded_blocks(markdown_content)
            markdown_content = _strip_known_low_value_sections(markdown_content)
            markdown_content = _expand_mkdocstrings_references(markdown_content)

            # Add file separator and content
            output.append(f'\n\n---\n# Source: {file_path}\n---\n\n')
            output.append(markdown_content)
            pages_included += 1
            included_paths.add(file_path)

        # Append markdown pages not present in nav
        for source_file in sorted(docs_dir.rglob('*.md')):
            rel_path = source_file.relative_to(docs_dir).as_posix()
            if rel_path in included_paths:
                continue

            log.warning(f'{rel_path} not in nav order, appending at end')
            markdown_content = source_file.read_text(encoding='utf-8')
            markdown_content = _strip_llms_excluded_blocks(markdown_content)
            markdown_content = _strip_known_low_value_sections(markdown_content)
            markdown_content = _expand_mkdocstrings_references(markdown_content)

            output.append(f'\n\n---\n# Source: {rel_path}\n---\n\n')
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
    finally:
        # Clear state for potential subsequent builds (e.g., during serve)
        _nav_order.clear()


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
- [API Reference]({site_url}/api/): Auto-generated Python API documentation
- [Compiler Architecture][1]: Core compiler design and data flow
- [Release Process][2]: Tag-based release and publishing workflow

[1]: https://github.com/strawgate/kb-yaml-to-lens/blob/main/packages/kb-dashboard-core/docs/compiler-architecture.md
[2]: https://github.com/strawgate/kb-yaml-to-lens/blob/main/RELEASE.md
"""
