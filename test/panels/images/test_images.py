"""Test the compilation of image panels from config models to view models."""

from inline_snapshot import snapshot

from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.images.compile import compile_image_panel_config
from dashboard_compiler.panels.images.config import ImagePanel
from test.panels.images.test_images_data import (
    CASE_URL_IMAGE,
    CASE_URL_IMAGE_ALT_TEXT,
    CASE_URL_IMAGE_BACKGROUND_COLOR,
    CASE_URL_IMAGE_FILL,
    CASE_URL_IMAGE_SIZING_COVER,
    CASE_URL_IMAGE_SIZING_NONE,
)


async def test_compile_image_panel_url() -> None:
    """Test the compilation of a basic image panel with URL."""
    config, _ = CASE_URL_IMAGE
    panel_grid = Grid(x=0, y=0, w=24, h=10)
    image_panel = ImagePanel(grid=panel_grid, **config)
    _, kbn_panel_config = compile_image_panel_config(image_panel=image_panel)
    kbn_panel_as_dict = kbn_panel_config.model_dump(by_alias=True)
    assert kbn_panel_as_dict == snapshot(
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


async def test_compile_image_panel_url_sizing_cover() -> None:
    """Test the compilation of an image panel with URL and cover sizing."""
    config, _ = CASE_URL_IMAGE_SIZING_COVER
    panel_grid = Grid(x=0, y=0, w=24, h=10)
    image_panel = ImagePanel(grid=panel_grid, **config)
    _, kbn_panel_config = compile_image_panel_config(image_panel=image_panel)
    kbn_panel_as_dict = kbn_panel_config.model_dump(by_alias=True)
    assert kbn_panel_as_dict == snapshot(
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


async def test_compile_image_panel_url_fill() -> None:
    """Test the compilation of an image panel with URL and fill sizing."""
    config, _ = CASE_URL_IMAGE_FILL
    panel_grid = Grid(x=0, y=0, w=24, h=10)
    image_panel = ImagePanel(grid=panel_grid, **config)
    _, kbn_panel_config = compile_image_panel_config(image_panel=image_panel)
    kbn_panel_as_dict = kbn_panel_config.model_dump(by_alias=True)
    assert kbn_panel_as_dict == snapshot(
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


async def test_compile_image_panel_url_sizing_none() -> None:
    """Test the compilation of an image panel with URL and none sizing."""
    config, _ = CASE_URL_IMAGE_SIZING_NONE
    panel_grid = Grid(x=0, y=0, w=24, h=10)
    image_panel = ImagePanel(grid=panel_grid, **config)
    _, kbn_panel_config = compile_image_panel_config(image_panel=image_panel)
    kbn_panel_as_dict = kbn_panel_config.model_dump(by_alias=True)
    assert kbn_panel_as_dict == snapshot(
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


async def test_compile_image_panel_url_alt_text() -> None:
    """Test the compilation of an image panel with URL and alt text."""
    config, _ = CASE_URL_IMAGE_ALT_TEXT
    panel_grid = Grid(x=0, y=0, w=24, h=10)
    image_panel = ImagePanel(grid=panel_grid, **config)
    _, kbn_panel_config = compile_image_panel_config(image_panel=image_panel)
    kbn_panel_as_dict = kbn_panel_config.model_dump(by_alias=True)
    assert kbn_panel_as_dict == snapshot(
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


async def test_compile_image_panel_url_background_color() -> None:
    """Test the compilation of an image panel with URL and background color."""
    config, _ = CASE_URL_IMAGE_BACKGROUND_COLOR
    panel_grid = Grid(x=0, y=0, w=24, h=10)
    image_panel = ImagePanel(grid=panel_grid, **config)
    _, kbn_panel_config = compile_image_panel_config(image_panel=image_panel)
    kbn_panel_as_dict = kbn_panel_config.model_dump(by_alias=True)
    assert kbn_panel_as_dict == snapshot(
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
