"""Test the compilation of image panels from config models to view models."""

from typing import Any

from inline_snapshot import snapshot

from dashboard_compiler.panels.images.compile import compile_image_panel_config
from dashboard_compiler.panels.images.config import ImagePanel


def compile_image_panel_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    """Compile image panel config and return dict for snapshot testing."""
    image_panel = ImagePanel(size={'w': 24, 'h': 10}, position={'x': 0, 'y': 0}, **config)
    _, kbn_panel_config = compile_image_panel_config(image_panel=image_panel)
    return kbn_panel_config.model_dump(by_alias=True)


def test_compile_image_panel_url() -> None:
    """Test the compilation of a basic image panel with URL."""
    result = compile_image_panel_snapshot(
        {'image': {'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg'}}
    )
    assert result == snapshot(
        {
            'enhancements': {'dynamicActions': {'events': []}},
            'imageConfig': {
                'src': {'type': 'url', 'url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg'},
                'altText': '',
                'backgroundColor': '',
                'sizing': {'objectFit': 'contain'},
            },
        }
    )


def test_compile_image_panel_url_sizing_cover() -> None:
    """Test the compilation of an image panel with URL and cover sizing."""
    result = compile_image_panel_snapshot(
        {'image': {'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg', 'fit': 'cover'}}
    )
    assert result == snapshot(
        {
            'enhancements': {'dynamicActions': {'events': []}},
            'imageConfig': {
                'src': {'type': 'url', 'url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg'},
                'altText': '',
                'backgroundColor': '',
                'sizing': {'objectFit': 'cover'},
            },
        }
    )


def test_compile_image_panel_url_fill() -> None:
    """Test the compilation of an image panel with URL and fill sizing."""
    result = compile_image_panel_snapshot(
        {'image': {'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg', 'fit': 'fill'}}
    )
    assert result == snapshot(
        {
            'enhancements': {'dynamicActions': {'events': []}},
            'imageConfig': {
                'src': {'type': 'url', 'url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg'},
                'altText': '',
                'backgroundColor': '',
                'sizing': {'objectFit': 'fill'},
            },
        }
    )


def test_compile_image_panel_url_sizing_none() -> None:
    """Test the compilation of an image panel with URL and none sizing."""
    result = compile_image_panel_snapshot(
        {'image': {'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg', 'fit': 'none'}}
    )
    assert result == snapshot(
        {
            'enhancements': {'dynamicActions': {'events': []}},
            'imageConfig': {
                'src': {'type': 'url', 'url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg'},
                'altText': '',
                'backgroundColor': '',
                'sizing': {'objectFit': 'none'},
            },
        }
    )


def test_compile_image_panel_url_alt_text() -> None:
    """Test the compilation of an image panel with URL and alt text."""
    result = compile_image_panel_snapshot(
        {
            'image': {
                'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg',
                'description': 'this is the alt text',
            },
        }
    )
    assert result == snapshot(
        {
            'enhancements': {'dynamicActions': {'events': []}},
            'imageConfig': {
                'src': {'type': 'url', 'url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg'},
                'altText': 'this is the alt text',
                'backgroundColor': '',
                'sizing': {'objectFit': 'contain'},
            },
        }
    )


def test_compile_image_panel_url_background_color() -> None:
    """Test the compilation of an image panel with URL and background color."""
    result = compile_image_panel_snapshot(
        {
            'image': {
                'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg',
                'background_color': '#a53c3c',
            }
        }
    )
    assert result == snapshot(
        {
            'enhancements': {'dynamicActions': {'events': []}},
            'imageConfig': {
                'src': {'type': 'url', 'url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg'},
                'altText': '',
                'backgroundColor': '#a53c3c',
                'sizing': {'objectFit': 'contain'},
            },
        }
    )
