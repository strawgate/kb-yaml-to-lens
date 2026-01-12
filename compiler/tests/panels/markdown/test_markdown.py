"""Test the compilation of markdown panels from config models to view models."""

from typing import Any

from inline_snapshot import snapshot

from dashboard_compiler.panels.markdown.compile import compile_markdown_panel_config
from dashboard_compiler.panels.markdown.config import MarkdownPanel


def compile_markdown_panel_snapshot(config: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compile markdown panel config and return dict for snapshot testing."""
    markdown_panel = MarkdownPanel(size={'w': 24, 'h': 10}, position={'x': 0, 'y': 0}, **config)
    kbn_references, kbn_panel_config = compile_markdown_panel_config(markdown_panel=markdown_panel)
    kbn_panel_as_dict = kbn_panel_config.model_dump(by_alias=True)
    kbn_references_as_dicts = [ref.model_dump(by_alias=True) for ref in kbn_references]
    return kbn_references_as_dicts, kbn_panel_as_dict


def test_compile_markdown_panel_basic() -> None:
    """Test the compilation of a basic markdown panel."""
    references, result = compile_markdown_panel_snapshot(
        {
            'markdown': {
                'content': '# default',
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'enhancements': {'dynamicActions': {'events': []}},
            'savedVis': {
                'id': '',
                'title': '',
                'description': '',
                'type': 'markdown',
                'params': {'fontSize': 12, 'openLinksInNewTab': False, 'markdown': '# default'},
                'uiState': {},
                'data': {'aggs': [], 'searchSource': {'query': {'query': '', 'language': 'kuery'}, 'filter': []}},
            },
        }
    )


def test_compile_markdown_panel_with_description() -> None:
    """Test the compilation of a markdown panel with description."""
    references, result = compile_markdown_panel_snapshot(
        {
            'description': 'description',
            'markdown': {
                'content': 'title and description',
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'enhancements': {'dynamicActions': {'events': []}},
            'savedVis': {
                'id': '',
                'title': '',
                'description': 'description',
                'type': 'markdown',
                'params': {'fontSize': 12, 'openLinksInNewTab': False, 'markdown': 'title and description'},
                'uiState': {},
                'data': {'aggs': [], 'searchSource': {'query': {'query': '', 'language': 'kuery'}, 'filter': []}},
            },
        }
    )


def test_compile_markdown_panel_custom_font_size() -> None:
    """Test the compilation of a markdown panel with custom font size."""
    references, result = compile_markdown_panel_snapshot(
        {
            'title': 'Important Note',
            'markdown': {
                'content': '# large font',
                'font_size': 18,
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'enhancements': {'dynamicActions': {'events': []}},
            'savedVis': {
                'id': '',
                'title': 'Important Note',
                'description': '',
                'type': 'markdown',
                'params': {'fontSize': 18, 'openLinksInNewTab': False, 'markdown': '# large font'},
                'uiState': {},
                'data': {'aggs': [], 'searchSource': {'query': {'query': '', 'language': 'kuery'}, 'filter': []}},
            },
        }
    )


def test_compile_markdown_panel_new_tab() -> None:
    """Test the compilation of a markdown panel which opens links in new tab."""
    references, result = compile_markdown_panel_snapshot(
        {
            'markdown': {
                'content': '# new_tab',
                'links_in_new_tab': True,
            },
        }
    )
    assert references == snapshot([])
    assert result == snapshot(
        {
            'enhancements': {'dynamicActions': {'events': []}},
            'savedVis': {
                'id': '',
                'title': '',
                'description': '',
                'type': 'markdown',
                'params': {'fontSize': 12, 'openLinksInNewTab': True, 'markdown': '# new_tab'},
                'uiState': {},
                'data': {'aggs': [], 'searchSource': {'query': {'query': '', 'language': 'kuery'}, 'filter': []}},
            },
        }
    )
