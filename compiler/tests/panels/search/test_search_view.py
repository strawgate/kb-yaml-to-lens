"""Tests for Search panel view models."""

import pytest
from inline_snapshot import snapshot
from pydantic import ValidationError

from dashboard_compiler.panels.search.view import (
    KbnSearchEmbeddableConfig,
    KbnSearchPanel,
)


class TestKbnSearchEmbeddableConfig:
    """Tests for KbnSearchEmbeddableConfig model."""

    def test_creates_with_default_enhancements(self) -> None:
        """Test that KbnSearchEmbeddableConfig creates with default empty enhancements."""
        config = KbnSearchEmbeddableConfig(savedSearchRefName='search:test-id')
        assert config.model_dump() == snapshot({'enhancements': {}, 'savedSearchRefName': 'search:test-id'})

    def test_creates_with_custom_enhancements(self) -> None:
        """Test that KbnSearchEmbeddableConfig creates with custom enhancements."""
        enhancements = {'dynamicActions': {'events': []}}
        config = KbnSearchEmbeddableConfig(savedSearchRefName='search:test-id', enhancements=enhancements)
        assert config.model_dump() == snapshot({'enhancements': {'dynamicActions': {'events': []}}, 'savedSearchRefName': 'search:test-id'})

    def test_requires_saved_search_ref_name(self) -> None:
        """Test that savedSearchRefName is required."""
        with pytest.raises(ValidationError, match='savedSearchRefName'):
            KbnSearchEmbeddableConfig()  # type: ignore[call-arg]


class TestKbnSearchPanel:
    """Tests for KbnSearchPanel model."""

    def test_creates_search_panel_with_required_fields(self) -> None:
        """Test that KbnSearchPanel creates with required fields and correct type."""
        panel = KbnSearchPanel(
            gridData={'x': 0, 'y': 0, 'w': 24, 'h': 15, 'i': 'panel-1'},
            panelIndex='panel-1',
            embeddableConfig=KbnSearchEmbeddableConfig(savedSearchRefName='search:test-id'),
        )
        assert panel.model_dump() == snapshot(
            {
                'type': 'search',
                'gridData': {'x': 0, 'y': 0, 'w': 24, 'h': 15, 'i': 'panel-1'},
                'panelIndex': 'panel-1',
                'embeddableConfig': {'enhancements': {}, 'savedSearchRefName': 'search:test-id'},
            }
        )

    def test_requires_embeddable_config(self) -> None:
        """Test that embeddableConfig is required."""
        with pytest.raises(ValidationError, match='embeddableConfig'):
            KbnSearchPanel(
                gridData={'x': 0, 'y': 0, 'w': 24, 'h': 15, 'i': 'panel-1'},
                panelIndex='panel-1',
            )  # type: ignore[call-arg]

    def test_requires_grid_data(self) -> None:
        """Test that gridData is required."""
        with pytest.raises(ValidationError, match='gridData'):
            KbnSearchPanel(
                panelIndex='panel-1',
                embeddableConfig=KbnSearchEmbeddableConfig(savedSearchRefName='search:test-id'),
            )  # type: ignore[call-arg]

    def test_requires_panel_index(self) -> None:
        """Test that panelIndex is required."""
        with pytest.raises(ValidationError, match='panelIndex'):
            KbnSearchPanel(
                gridData={'x': 0, 'y': 0, 'w': 24, 'h': 15, 'i': 'panel-1'},
                embeddableConfig=KbnSearchEmbeddableConfig(savedSearchRefName='search:test-id'),
            )  # type: ignore[call-arg]
