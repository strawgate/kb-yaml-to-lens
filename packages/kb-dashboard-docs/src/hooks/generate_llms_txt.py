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
_LLMS_FULL_EXCLUDE_PREFIXES: tuple[str, ...] = ('api/',)
_LLMS_FULL_EXCLUDE_FILES: tuple[str, ...] = ('vscode-extension.md', 'programmatic-usage.md')
_LLMS_TXT_EXCLUDE_FILES: tuple[str, ...] = ('examples/index.md', 'programmatic-usage.md')
_DEFAULT_LLMS_FULL_NAV: tuple[str, ...] = (
    'index.md',
    'CLI.md',
    'examples/index.md',
    'dashboard/dashboard.md',
    'panels/base.md',
    'panels/auto-layout.md',
    'panels/drilldowns.md',
    'panels/links.md',
    'panels/markdown.md',
    'panels/section.md',
    'panels/lens.md',
    'panels/esql.md',
    'panels/datatable.md',
    'panels/gauge.md',
    'panels/heatmap.md',
    'panels/metric.md',
    'panels/mosaic.md',
    'panels/pie.md',
    'panels/tagcloud.md',
    'panels/xy.md',
    'panels/image.md',
    'panels/search.md',
    'controls/config.md',
    'filters/config.md',
    'queries/config.md',
    'guides/index.md',
    'guides/breaking-changes.md',
    'guides/dashboard-decompiling-guide.md',
    'guides/dashboard-style-guide.md',
    'guides/esql-language-reference.md',
    'guides/otel-dashboard-guide.md',
    'guides/color-assignments.md',
    'guides/legend-configuration.md',
    'guides/esql-views.md',
)
_GUIDE_PATH_TO_NAME: dict[str, str] = {
    'guides/breaking-changes.md': 'breaking-changes',
    'guides/color-assignments.md': 'color-assignments',
    'guides/esql-views.md': 'esql-views',
    'guides/legend-configuration.md': 'legend-configuration',
    'guides/esql-language-reference.md': 'esql-language-reference',
    'guides/otel-dashboard-guide.md': 'otel-dashboard-guide',
    'guides/dashboard-decompiling-guide.md': 'dashboard-decompiling-guide',
    'guides/dashboard-style-guide.md': 'dashboard-style-guide',
}


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


def _normalize_doc_path(path: str) -> str:
    """Convert mkdocs source path to site URL path."""
    normalized = path.lstrip('/')
    if normalized.endswith('index.md'):
        return normalized[: -len('index.md')]
    if normalized.endswith('.md'):
        return normalized[: -len('.md')] + '/'
    return normalized


def _render_nav_links(
    nav_item: str | dict[str, Any] | list[Any],
    site_url: str,
    lines: list[str],
    depth: int = 0,
) -> None:
    """Render MkDocs nav structure as nested markdown links."""
    indent = '  ' * depth
    if isinstance(nav_item, str):
        if nav_item in _LLMS_TXT_EXCLUDE_FILES:
            return
        title = Path(nav_item).stem.replace('-', ' ').replace('_', ' ').title()
        lines.append(f'{indent}- [{title}]({site_url}/{_normalize_doc_path(nav_item)})')
        return

    if isinstance(nav_item, dict):
        for title, child in nav_item.items():
            if isinstance(child, str):
                if child in _LLMS_TXT_EXCLUDE_FILES:
                    continue
                lines.append(f'{indent}- [{title}]({site_url}/{_normalize_doc_path(child)})')
            else:
                lines.append(f'{indent}- **{title}**')
                _render_nav_links(child, site_url, lines, depth + 1)
        return

    if isinstance(nav_item, list):
        for child in nav_item:
            _render_nav_links(child, site_url, lines, depth)


def _render_guide_reference(file_path: str) -> str:
    """Render llms-full placeholder text for guide content."""
    guide_name = _GUIDE_PATH_TO_NAME[file_path]
    return (
        'Guide content is available via the CLI and intentionally excluded from llms-full.txt.\n\n'
        'Use:\n'
        '- `kb-dashboard docs list-guides`\n'
        f'- `kb-dashboard docs guide {guide_name}`'
    )


def _get_llms_full_nav(config: MkDocsConfig) -> list[str]:
    """Return llms-full page order from mkdocs extra.llms_nav or fallback default."""
    extra: dict[str, Any] = config.extra or {}  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    llms_nav = extra.get('llms_nav')
    if isinstance(llms_nav, list) and all(isinstance(item, str) for item in llms_nav):
        return list(llms_nav)
    return list(_DEFAULT_LLMS_FULL_NAV)


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
_POEM_SECTION_RE = re.compile(r'(?ms)^##\s+A Poem[^\n]*\n[\s\S]*?(?=^\s*---\s*$)')
_HTML_COMMENT_RE = re.compile(r'(?ms)<!--.*?-->')
_MKDOCS_INCLUDE_DIRECTIVE_RE = re.compile(r'(?m)^\s*--8<--\s+["\'][^"\']+["\']\s*$\n?')


def _format_annotation(annotation: Any) -> str:
    """Format type annotation for concise markdown output."""
    if annotation is inspect._empty:
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
                annotation = _format_annotation(getattr(field, 'annotation', inspect._empty))
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
    markdown = _LLMS_EXCLUDE_BLOCK_RE.sub('', markdown)
    return _LLMS_EXCLUDE_INLINE_RE.sub('', markdown)


def _strip_known_low_value_sections(markdown: str) -> str:
    """Remove sections that are useful for humans but noisy for llms-full."""
    return _POEM_SECTION_RE.sub('', markdown)


def _strip_nonportable_markdown(markdown: str) -> str:
    """Remove markdown constructs that don't render in plain text contexts."""
    markdown = _HTML_COMMENT_RE.sub('', markdown)
    return _MKDOCS_INCLUDE_DIRECTIVE_RE.sub('', markdown)


def on_post_build(config: MkDocsConfig) -> None:
    """Generate llms-full.txt by post-processing markdown sources.

    This is option 3 from issue #1234: selectively resolve mkdocstrings references
    in a second pass instead of relying on full HTML conversion.
    """
    try:
        docs_dir = Path(config.docs_dir)
        site_dir = Path(config.site_dir)

        output: list[str] = []

        # Add header
        output.append('# Dashboard Compiler - Complete Documentation\n\n')
        output.append('> This file contains all documentation for the Dashboard Compiler project.\n\n')
        output.append('---\n\n')

        llms_full_nav = _get_llms_full_nav(config)

        # Concatenate pages in llms-specific navigation order
        pages_included = 0
        for file_path in llms_full_nav:
            if file_path.startswith(_LLMS_FULL_EXCLUDE_PREFIXES):
                continue
            if file_path in _LLMS_FULL_EXCLUDE_FILES:
                continue

            if file_path in _GUIDE_PATH_TO_NAME:
                output.append(f'\n\n---\n# Source: {file_path}\n---\n\n')
                output.append(_render_guide_reference(file_path))
                pages_included += 1
                continue

            source_file = docs_dir / file_path
            if not source_file.exists():
                log.warning(f'{file_path} not found in docs dir, skipping...')
                continue

            markdown_content = source_file.read_text(encoding='utf-8')
            markdown_content = _strip_llms_excluded_blocks(markdown_content)
            markdown_content = _strip_known_low_value_sections(markdown_content)
            markdown_content = _strip_nonportable_markdown(markdown_content)
            markdown_content = _expand_mkdocstrings_references(markdown_content)

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
    finally:
        # Clear state for potential subsequent builds (e.g., during serve)
        _nav_order.clear()


def generate_llms_txt_content(config: MkDocsConfig) -> str:
    """Generate llms.txt navigation content from MkDocs nav hierarchy."""
    if config.site_url is None:
        msg = 'site_url is required'
        raise ValueError(msg)

    site_url: str = config.site_url.rstrip('/')
    lines: list[str] = [
        '# Dashboard Compiler',
        '',
        '> Convert human-friendly YAML dashboard definitions into Kibana NDJSON format.',
        '> Navigation generated from MkDocs `nav` to avoid hardcoded drift.',
        '',
        '## Site Navigation',
        '',
    ]
    nav: list[Any] = config.nav or []  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    _render_nav_links(nav, site_url, lines)
    lines.extend(
        [
            '',
            '## Additional References',
            '',
            f'- [llms-full.txt]({site_url}/llms-full.txt): Complete docs corpus for LLM context',
            '- [Compiler Architecture](https://github.com/strawgate/kb-yaml-to-lens/blob/main/packages/kb-dashboard-core/docs/compiler-architecture.md)',
            '- [Release Process](https://github.com/strawgate/kb-yaml-to-lens/blob/main/RELEASE.md)',
            '',
        ]
    )
    return '\n'.join(lines)
