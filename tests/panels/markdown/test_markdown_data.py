"""Test data for markdown panel compilation tests."""

CASE_MARKDOWN = (
    {
        'type': 'markdown',
        'content': '# default',
    },
    {
        'enhancements': {'dynamicActions': {'events': []}},
        'savedVis': {
            'id': '',
            'title': '',
            'description': '',
            'type': 'markdown',
            'params': {'fontSize': 12, 'openLinksInNewTab': False, 'markdown': '# default'},
            'uiState': {},
            'data': {'aggs': [], 'searchSource': {'query': {'query': '', 'language': 'lucene'}, 'filter': []}},
        },
    },
    [],
)
"""Tuple[Config as Dict, View as Dict, References as List] for a basic markdown panel."""

CASE_MARKDOWN_DESCRIPTION = (
    {
        'type': 'markdown',
        'description': 'description',
        'content': 'title and description',
    },
    {
        'enhancements': {'dynamicActions': {'events': []}},
        'savedVis': {
            'id': '',
            'title': '',
            'description': 'description',
            'type': 'markdown',
            'params': {'fontSize': 12, 'openLinksInNewTab': False, 'markdown': 'title and description'},
            'uiState': {},
            'data': {'aggs': [], 'searchSource': {'query': {'query': '', 'language': 'lucene'}, 'filter': []}},
        },
    },
    [],
)
"""Tuple[Config as Dict, View as Dict, References as List] for a markdown panel with description."""

CASE_MARKDOWN_CUSTOM_FONT_SIZE = (
    {
        'type': 'markdown',
        'title': 'Important Note',
        'content': '# large font',
        'font_size': 18,
    },
    {
        'enhancements': {'dynamicActions': {'events': []}},
        'savedVis': {
            'id': '',
            'title': 'Important Note',
            'description': '',
            'type': 'markdown',
            'params': {'fontSize': 18, 'openLinksInNewTab': False, 'markdown': '# large font'},
            'uiState': {},
            'data': {'aggs': [], 'searchSource': {'query': {'query': '', 'language': 'lucene'}, 'filter': []}},
        },
    },
    [],
)
"""Tuple[Config as Dict, View as Dict, References as List] for a markdown panel with custom font size."""

CASE_MARKDOWN_NEW_TAB = (
    {
        'type': 'markdown',
        'content': '# new_tab',
        'links_in_new_tab': True,
    },
    {
        'enhancements': {'dynamicActions': {'events': []}},
        'savedVis': {
            'id': '',
            'title': '',
            'description': '',
            'type': 'markdown',
            'params': {'fontSize': 12, 'openLinksInNewTab': True, 'markdown': '# new_tab'},
            'uiState': {},
            'data': {'aggs': [], 'searchSource': {'query': {'query': '', 'language': 'lucene'}, 'filter': []}},
        },
    },
    [],
)
"""Tuple[Config as Dict, View as Dict, References as List] for a markdown panel which opens links in new tab."""


TEST_CASES = [
    CASE_MARKDOWN,
    CASE_MARKDOWN_DESCRIPTION,
    CASE_MARKDOWN_CUSTOM_FONT_SIZE,
    CASE_MARKDOWN_NEW_TAB,
]

TEST_CASE_IDS = [
    'Basic Markdown Panel',
    'Markdown Panel with Description',
    'Markdown Panel with Custom Font Size',
    'Markdown Panel which opens Links in New Tab',
]
