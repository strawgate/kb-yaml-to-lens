"""Test data for links panel compilation tests."""

CASE_BASIC_URL_LINK = (
    {
        'type': 'links',
        'links': [
            {'url': 'https://elastic.co'},
        ],
    },
    {
        'attributes': {
            'layout': 'horizontal',
            'links': [
                {
                    'label': '',
                    'type': 'externalLink',
                    'id': '16da766e-c67a-4d2e-9eec-c477af79f374',
                    'destination': 'https://elastic.co',
                    'order': 0,
                }
            ],
        },
        'enhancements': {},
    },
    [],
)
"""Tuple[Config as Dict, View as Dict, References as List] for a basic URL link with no label."""


CASE_BASIC_URL_LINK_CUSTOM_ID = (
    {
        'type': 'links',
        'links': [
            {
                'url': 'https://elastic.co',
                'id': '16da766e-c67a-4d2e-9eec-c477af79f374',
            },
        ],
    },
    {
        'attributes': {
            'layout': 'horizontal',
            'links': [
                {
                    'label': '',
                    'type': 'externalLink',
                    'id': '16da766e-c67a-4d2e-9eec-c477af79f374',
                    'destination': 'https://elastic.co',
                    'order': 0,
                }
            ],
        },
        'enhancements': {},
    },
    [],
)
"""Tuple[Config as Dict, View as Dict, References as List] for a custom ID"""


CASE_BASIC_URL_LINK_LABEL = (
    {
        'type': 'links',
        'links': [
            {'url': 'https://elastic.co', 'label': 'Custom Label'},
        ],
    },
    {
        'attributes': {
            'layout': 'horizontal',
            'links': [
                {
                    'label': 'Custom Label',
                    'type': 'externalLink',
                    'id': '16da766e-c67a-4d2e-9eec-c477af79f374',
                    'destination': 'https://elastic.co',
                    'order': 0,
                }
            ],
        },
        'enhancements': {},
    },
    [],
)
"""Tuple[Config as Dict, View as Dict, References as List] for a basic URL link with a label."""

CASE_BASIC_URL_LINK_INVERTED_OPTIONS = (
    {
        'type': 'links',
        'links': [
            {'url': 'https://elastic.co', 'label': 'Custom Label', 'new_tab': False, 'encode': False},
        ],
    },
    {
        'attributes': {
            'layout': 'horizontal',
            'links': [
                {
                    'label': 'Custom Label',
                    'type': 'externalLink',
                    'id': '16da766e-c67a-4d2e-9eec-c477af79f374',
                    'destination': 'https://elastic.co',
                    'order': 0,
                    'options': {'encodeUrl': False, 'openInNewTab': False},
                }
            ],
        },
        'enhancements': {},
    },
    [],
)
"""Tuple[Config as Dict, View as Dict, References as List] for a basic URL link with all options inverted."""

CASE_BASIC_DASHBOARD_LINK = (
    {
        'type': 'links',
        'id': '74522ed1-eb91-4b8a-bcbe-ffa0ff9c9abf',
        'layout': 'vertical',
        'links': [
            {'dashboard': '71a1e537-15ed-4891-b102-4ef0f314a037', 'label': 'Go to Dashboard', 'id': 'f1057dc0-1132-4143-8a58-ccbc853aee46'},
        ],
    },
    {
        'attributes': {
            'layout': 'vertical',
            'links': [
                {
                    'label': 'Go to Dashboard',
                    'type': 'dashboardLink',
                    'id': 'f1057dc0-1132-4143-8a58-ccbc853aee46',
                    'order': 0,
                    'destinationRefName': 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard',
                },
            ],
        },
        'enhancements': {},
    },
    [
        {
            'id': '71a1e537-15ed-4891-b102-4ef0f314a037',  # External dashboard ID
            'name': 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard',
            'type': 'dashboard',
        },
    ],
)
"""Tuple[Config as Dict, View as Dict, References as List] for a basic Dashboard link."""


CASE_BASIC_DASHBOARD_LINK_INVERTED_OPTIONS = (
    {
        'type': 'links',
        'id': '71a1e537-15ed-4891-b102-4ef0f314a037',
        'layout': 'vertical',
        'links': [
            {
                'dashboard': '71a1e537-15ed-4891-b102-4ef0f314a037',
                'label': 'Go to Dashboard',
                'id': 'f1057dc0-1132-4143-8a58-ccbc853aee46',
                'with_time': False,
                'with_filters': False,
                'new_tab': True,
            },
        ],
    },
    {
        'attributes': {
            'layout': 'vertical',
            'links': [
                {
                    'label': 'Go to Dashboard',
                    'type': 'dashboardLink',
                    'id': 'f1057dc0-1132-4143-8a58-ccbc853aee46',
                    'order': 0,
                    'destinationRefName': 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard',
                    'options': {'openInNewTab': True, 'useCurrentDateRange': False, 'useCurrentFilters': False},
                },
            ],
        },
        'enhancements': {},
    },
    [
        {
            'id': '71a1e537-15ed-4891-b102-4ef0f314a037',  # External dashboard ID
            'name': 'link_f1057dc0-1132-4143-8a58-ccbc853aee46_dashboard',
            'type': 'dashboard',
        },
    ],
)
"""Tuple[Config as Dict, View as Dict, References as List] for a basic Dashboard link with all options inverted."""


TEST_CASES = [
    CASE_BASIC_URL_LINK,
    CASE_BASIC_URL_LINK_CUSTOM_ID,
    CASE_BASIC_URL_LINK_LABEL,
    CASE_BASIC_URL_LINK_INVERTED_OPTIONS,
    CASE_BASIC_DASHBOARD_LINK,
    CASE_BASIC_DASHBOARD_LINK_INVERTED_OPTIONS,
]

TEST_CASE_IDS = [
    'Basic URL Link',
    'Basic URL Link with Custom ID',
    'Basic URL Link with Label',
    'Basic URL Link with Inverted Options',
    'Basic Dashboard Link',
    'Basic Dashboard Link with Inverted Options',
]
