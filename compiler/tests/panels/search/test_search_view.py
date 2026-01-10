"""Tests for Search panel view models."""

from dashboard_compiler.panels.search.view import (
    KbnSearchEmbeddableConfig,
    KbnSearchPanel,
)


class TestKbnSearchEmbeddableConfig:
    """Tests for KbnSearchEmbeddableConfig model."""

    def test_creates_with_default_enhancements(self) -> None:
        """Test that KbnSearchEmbeddableConfig creates with default empty enhancements."""
        config = KbnSearchEmbeddableConfig(savedSearchRefName='search:test-id')
        assert config.enhancements == {}
        assert config.savedSearchRefName == 'search:test-id'

    def test_creates_with_custom_enhancements(self) -> None:
        """Test that KbnSearchEmbeddableConfig creates with custom enhancements."""
        enhancements = {'dynamicActions': {'events': []}}
        config = KbnSearchEmbeddableConfig(savedSearchRefName='search:test-id', enhancements=enhancements)
        assert config.enhancements == enhancements

    def test_serializes_to_dict(self) -> None:
        """Test that KbnSearchEmbeddableConfig serializes to dict correctly."""
        config = KbnSearchEmbeddableConfig(savedSearchRefName='search:test-id', enhancements={'test': 'value'})
        result = config.model_dump()
        assert result == {'enhancements': {'test': 'value'}, 'savedSearchRefName': 'search:test-id'}


class TestKbnSearchPanel:
    """Tests for KbnSearchPanel model."""

    def test_creates_search_panel_with_required_fields(self) -> None:
        """Test that KbnSearchPanel creates with required fields."""
        panel = KbnSearchPanel(
            gridData={'x': 0, 'y': 0, 'w': 24, 'h': 15, 'i': 'panel-1'},
            panelIndex='panel-1',
            embeddableConfig=KbnSearchEmbeddableConfig(savedSearchRefName='search:test-id'),
        )
        assert panel.type == 'search'
        assert panel.panelIndex == 'panel-1'

    def test_type_field_is_literal_search(self) -> None:
        """Test that type field is always 'search'."""
        panel = KbnSearchPanel(
            gridData={'x': 0, 'y': 0, 'w': 24, 'h': 15, 'i': 'panel-1'},
            panelIndex='panel-1',
            embeddableConfig=KbnSearchEmbeddableConfig(savedSearchRefName='search:test-id'),
        )
        assert panel.type == 'search'

    def test_serializes_to_dict_correctly(self) -> None:
        """Test that KbnSearchPanel serializes to dict correctly."""
        panel = KbnSearchPanel(
            gridData={'x': 0, 'y': 0, 'w': 24, 'h': 15, 'i': 'panel-1'},
            panelIndex='panel-1',
            embeddableConfig=KbnSearchEmbeddableConfig(savedSearchRefName='search:test-id'),
        )
        result = panel.model_dump()
        assert result['type'] == 'search'
        assert result['panelIndex'] == 'panel-1'
        assert result['embeddableConfig'] == {'enhancements': {}, 'savedSearchRefName': 'search:test-id'}
