"""Tests for Search panel view models."""

from dashboard_compiler.panels.search.view import (
    KbnSearchEmbeddableConfig,
    KbnSearchPanel,
)


class TestKbnSearchEmbeddableConfig:
    """Tests for KbnSearchEmbeddableConfig model."""

    def test_creates_with_default_enhancements(self) -> None:
        """Test that KbnSearchEmbeddableConfig creates with default empty enhancements."""
        config = KbnSearchEmbeddableConfig()
        assert config.enhancements == {}

    def test_creates_with_custom_enhancements(self) -> None:
        """Test that KbnSearchEmbeddableConfig creates with custom enhancements."""
        enhancements = {'dynamicActions': {'events': []}}
        config = KbnSearchEmbeddableConfig(enhancements=enhancements)
        assert config.enhancements == enhancements

    def test_serializes_to_dict(self) -> None:
        """Test that KbnSearchEmbeddableConfig serializes to dict correctly."""
        config = KbnSearchEmbeddableConfig(enhancements={'test': 'value'})
        result = config.model_dump()
        assert result == {'enhancements': {'test': 'value'}}


class TestKbnSearchPanel:
    """Tests for KbnSearchPanel model."""

    def test_creates_search_panel_with_required_fields(self) -> None:
        """Test that KbnSearchPanel creates with required fields."""
        panel = KbnSearchPanel(
            gridData={'x': 0, 'y': 0, 'w': 24, 'h': 15, 'i': 'panel-1'},
            panelIndex='panel-1',
            embeddableConfig=KbnSearchEmbeddableConfig(),
        )
        assert panel.type == 'search'
        assert panel.panelIndex == 'panel-1'

    def test_type_field_is_literal_search(self) -> None:
        """Test that type field is always 'search'."""
        panel = KbnSearchPanel(
            gridData={'x': 0, 'y': 0, 'w': 24, 'h': 15, 'i': 'panel-1'},
            panelIndex='panel-1',
            embeddableConfig=KbnSearchEmbeddableConfig(),
        )
        assert panel.type == 'search'

    def test_serializes_to_dict_correctly(self) -> None:
        """Test that KbnSearchPanel serializes to dict correctly."""
        panel = KbnSearchPanel(
            gridData={'x': 0, 'y': 0, 'w': 24, 'h': 15, 'i': 'panel-1'},
            panelIndex='panel-1',
            embeddableConfig=KbnSearchEmbeddableConfig(),
        )
        result = panel.model_dump()
        assert result['type'] == 'search'
        assert result['panelIndex'] == 'panel-1'
        assert result['embeddableConfig'] == {'enhancements': {}}
