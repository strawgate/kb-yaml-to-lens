"""Test panel type detection and discrimination."""

from typing import ClassVar

import pytest

from kb_dashboard_core.panels.types import get_panel_type


class TestGetPanelType:
    """Test the get_panel_type function for discriminated union validation."""

    def test_identifies_markdown_from_dict(self) -> None:
        """Test that markdown panel type is identified from a dict."""
        panel_dict = {'markdown': 'Some markdown content', 'position': {'x': 0, 'y': 0}, 'size': {'w': 12, 'h': 4}}
        assert get_panel_type(panel_dict) == 'markdown'

    def test_identifies_search_from_dict(self) -> None:
        """Test that search panel type is identified from a dict."""
        panel_dict = {'search': 'search-id', 'position': {'x': 0, 'y': 0}, 'size': {'w': 12, 'h': 4}}
        assert get_panel_type(panel_dict) == 'search'

    def test_identifies_links_from_dict(self) -> None:
        """Test that links panel type is identified from a dict."""
        panel_dict = {
            'links': [{'url': 'https://example.com', 'label': 'Example'}],
            'position': {'x': 0, 'y': 0},
            'size': {'w': 12, 'h': 4},
        }
        assert get_panel_type(panel_dict) == 'links'

    def test_identifies_image_from_dict(self) -> None:
        """Test that image panel type is identified from a dict."""
        panel_dict = {'image': 'https://example.com/image.png', 'position': {'x': 0, 'y': 0}, 'size': {'w': 12, 'h': 4}}
        assert get_panel_type(panel_dict) == 'image'

    def test_identifies_lens_from_dict(self) -> None:
        """Test that lens panel type is identified from a dict."""
        panel_dict = {'lens': {'charts': []}, 'position': {'x': 0, 'y': 0}, 'size': {'w': 12, 'h': 4}}
        assert get_panel_type(panel_dict) == 'lens'

    def test_identifies_esql_from_dict(self) -> None:
        """Test that esql panel type is identified from a dict."""
        panel_dict = {'esql': {'charts': []}, 'position': {'x': 0, 'y': 0}, 'size': {'w': 12, 'h': 4}}
        assert get_panel_type(panel_dict) == 'esql'

    def test_raises_error_for_unknown_dict(self) -> None:
        """Test that an error is raised for a dict with unknown keys."""
        panel_dict = {'unknown': 'value', 'position': {'x': 0, 'y': 0}, 'size': {'w': 12, 'h': 4}}
        with pytest.raises(ValueError, match='Cannot determine panel type from dict with keys'):
            _ = get_panel_type(panel_dict)

    def test_raises_error_for_empty_dict(self) -> None:
        """Test that an error is raised for an empty dict."""
        panel_dict: dict[str, object] = {}
        with pytest.raises(ValueError, match='Cannot determine panel type from dict with keys'):
            _ = get_panel_type(panel_dict)

    def test_identifies_panel_from_object_with_markdown_attr(self) -> None:
        """Test that panel type is identified from an object with markdown attribute."""

        class MockPanel:
            markdown: str = 'Some content'

        assert get_panel_type(MockPanel()) == 'markdown'

    def test_identifies_panel_from_object_with_search_attr(self) -> None:
        """Test that panel type is identified from an object with search attribute."""

        class MockPanel:
            search: str = 'search-id'

        assert get_panel_type(MockPanel()) == 'search'

    def test_identifies_panel_from_object_with_links_config_attr(self) -> None:
        """Test that panel type is identified from an object with links_config attribute."""

        class MockPanel:
            links_config: ClassVar[list[object]] = []

        assert get_panel_type(MockPanel()) == 'links'

    def test_identifies_panel_from_object_with_image_attr(self) -> None:
        """Test that panel type is identified from an object with image attribute."""

        class MockPanel:
            image: str = 'https://example.com/image.png'

        assert get_panel_type(MockPanel()) == 'image'

    def test_identifies_panel_from_object_with_lens_attr(self) -> None:
        """Test that panel type is identified from an object with lens attribute."""

        class MockPanel:
            lens: ClassVar[dict[str, object]] = {}

        assert get_panel_type(MockPanel()) == 'lens'

    def test_identifies_panel_from_object_with_esql_attr(self) -> None:
        """Test that panel type is identified from an object with esql attribute."""

        class MockPanel:
            esql: ClassVar[dict[str, object]] = {}

        assert get_panel_type(MockPanel()) == 'esql'

    def test_raises_error_for_object_without_panel_attrs(self) -> None:
        """Test that an error is raised for an object without panel attributes."""

        class MockPanel:
            unknown: str = 'value'

        with pytest.raises(ValueError, match='Cannot determine panel type from object'):
            _ = get_panel_type(MockPanel())
