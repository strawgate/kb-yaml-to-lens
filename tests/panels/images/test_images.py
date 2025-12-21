"""Test the compilation of image panels from config models to view models."""

from typing import Any

import pytest
from inline_snapshot import snapshot

from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.images.compile import compile_image_panel_config
from dashboard_compiler.panels.images.config import ImagePanel


@pytest.fixture
def compile_image_panel_snapshot():
    """Fixture that returns a function to compile image panels and return dict for snapshot."""

    def _compile(config: dict[str, Any]) -> dict[str, Any]:
        panel_grid = Grid(x=0, y=0, w=24, h=10)
        image_panel = ImagePanel(grid=panel_grid, **config)
        _, kbn_panel_config = compile_image_panel_config(image_panel=image_panel)
        return kbn_panel_config.model_dump(by_alias=True)

    return _compile


def test_compile_image_panel_url(compile_image_panel_snapshot) -> None:
    """Test the compilation of a basic image panel with URL."""
    result = compile_image_panel_snapshot({'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg'})
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


def test_compile_image_panel_url_sizing_cover(compile_image_panel_snapshot) -> None:
    """Test the compilation of an image panel with URL and cover sizing."""
    result = compile_image_panel_snapshot(
        {'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg', 'fit': 'cover'}
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


def test_compile_image_panel_url_fill(compile_image_panel_snapshot) -> None:
    """Test the compilation of an image panel with URL and fill sizing."""
    result = compile_image_panel_snapshot(
        {'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg', 'fit': 'fill'}
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


def test_compile_image_panel_url_sizing_none(compile_image_panel_snapshot) -> None:
    """Test the compilation of an image panel with URL and none sizing."""
    result = compile_image_panel_snapshot(
        {'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg', 'fit': 'none'}
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


def test_compile_image_panel_url_alt_text(compile_image_panel_snapshot) -> None:
    """Test the compilation of an image panel with URL and alt text."""
    result = compile_image_panel_snapshot(
        {'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg', 'description': 'this is the alt text'}
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


def test_compile_image_panel_url_background_color(compile_image_panel_snapshot) -> None:
    """Test the compilation of an image panel with URL and background color."""
    result = compile_image_panel_snapshot(
        {'from_url': 'https://4.img-dpreview.com/files/p/E~TS1180x0~articles/3925134721/0266554465.jpeg', 'background_color': '#a53c3c'}
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
