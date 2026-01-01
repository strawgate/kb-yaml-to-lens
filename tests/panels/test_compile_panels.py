"""Test panel compilation functions."""

import pytest
from dirty_equals import IsUUID
from inline_snapshot import snapshot

from dashboard_compiler.panels.compile import compile_dashboard_panel, get_panel_type_name
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.images.config import ImagePanel, ImagePanelConfig
from dashboard_compiler.panels.links.config import LinksPanel, LinksPanelConfig, UrlLink
from dashboard_compiler.panels.markdown.config import MarkdownPanel, MarkdownPanelConfig
from dashboard_compiler.panels.search.config import SearchPanel, SearchPanelConfig


class TestGetPanelTypeName:
    """Test the get_panel_type_name function."""

    def test_returns_markdown_for_markdown_panel(self) -> None:
        """Test that 'markdown' is returned for a MarkdownPanel."""
        panel = MarkdownPanel(markdown=MarkdownPanelConfig(content='# Test'), grid=Grid(x=0, y=0, w=12, h=4))
        assert get_panel_type_name(panel) == 'markdown'

    def test_returns_links_for_links_panel(self) -> None:
        """Test that 'links' is returned for a LinksPanel."""
        panel = LinksPanel(links=LinksPanelConfig(links=[UrlLink(url='https://example.com')]), grid=Grid(x=0, y=0, w=12, h=4))
        assert get_panel_type_name(panel) == 'links'

    def test_returns_image_for_image_panel(self) -> None:
        """Test that 'image' is returned for an ImagePanel."""
        panel = ImagePanel(image=ImagePanelConfig(from_url='https://example.com/image.png'), grid=Grid(x=0, y=0, w=12, h=4))
        assert get_panel_type_name(panel) == 'image'

    def test_returns_search_for_search_panel(self) -> None:
        """Test that 'search' is returned for a SearchPanel."""
        panel = SearchPanel(search=SearchPanelConfig(saved_search_id='search-id'), grid=Grid(x=0, y=0, w=12, h=4))
        assert get_panel_type_name(panel) == 'search'


class TestCompileDashboardPanel:
    """Test the compile_dashboard_panel function."""

    def test_compiles_links_panel(self) -> None:
        """Test that a LinksPanel is compiled correctly."""
        panel = LinksPanel(
            links=LinksPanelConfig(links=[UrlLink(url='https://example.com', label='Example')]), grid=Grid(x=0, y=0, w=12, h=4)
        )
        _references, kbn_panel = compile_dashboard_panel(panel)

        assert kbn_panel.model_dump(by_alias=True) == snapshot(
            {
                'gridData': {'x': 0, 'y': 0, 'w': 12, 'h': 4, 'i': IsUUID},
                'embeddableConfig': {
                    'enhancements': {},
                    'attributes': {
                        'layout': 'horizontal',
                        'links': [
                            {
                                'id': IsUUID,
                                'order': 0,
                                'label': 'Example',
                                'type': 'externalLink',
                                'destination': 'https://example.com',
                            }
                        ],
                    },
                },
                'panelIndex': IsUUID,
                'type': 'links',
            }
        )

    def test_compiles_image_panel(self) -> None:
        """Test that an ImagePanel is compiled correctly."""
        panel = ImagePanel(image=ImagePanelConfig(from_url='https://example.com/image.png'), grid=Grid(x=0, y=0, w=12, h=4))
        _references, kbn_panel = compile_dashboard_panel(panel)

        assert kbn_panel.model_dump(by_alias=True) == snapshot(
            {
                'gridData': {'x': 0, 'y': 0, 'w': 12, 'h': 4, 'i': IsUUID},
                'embeddableConfig': {
                    'enhancements': {'dynamicActions': {'events': []}},
                    'imageConfig': {
                        'altText': '',
                        'backgroundColor': '',
                        'sizing': {'objectFit': 'contain'},
                        'src': {'type': 'url', 'url': 'https://example.com/image.png'},
                    },
                },
                'panelIndex': IsUUID,
                'type': 'image',
            }
        )

    def test_raises_not_implemented_for_search_panel(self) -> None:
        """Test that SearchPanel compilation raises NotImplementedError."""
        panel = SearchPanel(search=SearchPanelConfig(saved_search_id='search-id'), grid=Grid(x=0, y=0, w=12, h=4))

        with pytest.raises(NotImplementedError, match='Panel type SearchPanel is not yet supported'):
            _ = compile_dashboard_panel(panel)
