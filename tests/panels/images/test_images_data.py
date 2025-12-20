"""Test data for markdown panel compilation tests."""

CASE_URL_IMAGE = (
    {
        'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg',
    },
    {
        'enhancements': {'dynamicActions': {'events': []}},
        'imageConfig': {
            'src': {'type': 'url', 'url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg'},
            'altText': '',
            'backgroundColor': '',
            'sizing': {'objectFit': 'contain'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for a basic image panel with URL."""

CASE_URL_IMAGE_SIZING_COVER = (
    {
        'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg',
        'fit': 'cover',
    },
    {
        'enhancements': {'dynamicActions': {'events': []}},
        'imageConfig': {
            'src': {'type': 'url', 'url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg'},
            'altText': '',
            'backgroundColor': '',
            'sizing': {'objectFit': 'cover'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for a basic image panel with URL and cover sizing."""

CASE_URL_IMAGE_FILL = (
    {
        'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg',
        'fit': 'fill',
    },
    {
        'enhancements': {'dynamicActions': {'events': []}},
        'imageConfig': {
            'src': {'type': 'url', 'url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg'},
            'altText': '',
            'backgroundColor': '',
            'sizing': {'objectFit': 'fill'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for a basic image panel with URL and fill sizing."""

CASE_URL_IMAGE_SIZING_NONE = (
    {
        'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg',
        'fit': 'none',
    },
    {
        'enhancements': {'dynamicActions': {'events': []}},
        'imageConfig': {
            'src': {'type': 'url', 'url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg'},
            'altText': '',
            'backgroundColor': '',
            'sizing': {'objectFit': 'none'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for a basic image panel with URL and none sizing."""

CASE_URL_IMAGE_ALT_TEXT = (
    {
        'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg',
        'description': 'this is the alt text',
    },
    {
        'enhancements': {'dynamicActions': {'events': []}},
        'imageConfig': {
            'src': {'type': 'url', 'url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg'},
            'altText': 'this is the alt text',
            'backgroundColor': '',
            'sizing': {'objectFit': 'contain'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for a basic image panel with URL and alt text."""

CASE_URL_IMAGE_BACKGROUND_COLOR = (
    {
        'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg',
        'background_color': '#a53c3c',
    },
    {
        'enhancements': {'dynamicActions': {'events': []}},
        'imageConfig': {
            'src': {'type': 'url', 'url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg'},
            'altText': '',
            'backgroundColor': '#a53c3c',
            'sizing': {'objectFit': 'contain'},
        },
    },
)
"""Tuple[Config as Dict, View as Dict] for a basic image panel with URL and background color."""


TEST_CASES = [
    CASE_URL_IMAGE,
    CASE_URL_IMAGE_SIZING_COVER,
    CASE_URL_IMAGE_FILL,
    CASE_URL_IMAGE_SIZING_NONE,
    CASE_URL_IMAGE_ALT_TEXT,
    CASE_URL_IMAGE_BACKGROUND_COLOR,
]

TEST_CASE_IDS = [
    'URL Image',
    'URL Image Sizing Cover',
    'URL Image Fill',
    'URL Image Sizing None',
    'URL Image Alt Text',
    'URL Image Background Color',
]
