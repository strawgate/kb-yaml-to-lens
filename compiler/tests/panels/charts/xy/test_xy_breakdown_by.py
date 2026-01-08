"""Test breakdown_by functionality for XY charts."""

import pytest
from pydantic import ValidationError

from dashboard_compiler.panels.charts.xy.compile import compile_lens_xy_chart
from dashboard_compiler.panels.charts.xy.config import ESQLBarChart, LensBarChart


def test_xy_breakdown_by_single_field() -> None:
    """Test XY chart with a single breakdown_by field."""
    config = LensBarChart(
        type='bar',
        data_view='logs-*',
        metrics=[{'aggregation': 'count'}],
        breakdown_by=[{'field': 'service.name', 'type': 'values'}],
    )

    _layer_id, _columns, viz_state = compile_lens_xy_chart(config)

    # Single breakdown uses splitAccessor (backward compatible)
    assert len(viz_state.layers) == 1
    layer = viz_state.layers[0]
    assert layer.layerType == 'data'
    assert layer.splitAccessor is not None
    assert layer.splitAccessors is None


def test_xy_breakdown_by_multiple_fields() -> None:
    """Test XY chart with multiple breakdown_by fields."""
    config = LensBarChart(
        type='bar',
        data_view='logs-*',
        metrics=[{'aggregation': 'count'}],
        breakdown_by=[
            {'field': 'service.name', 'type': 'values'},
            {'field': 'host.name', 'type': 'values'},
        ],
    )

    _layer_id, _columns, viz_state = compile_lens_xy_chart(config)

    # Multiple breakdowns use splitAccessors (array)
    assert len(viz_state.layers) == 1
    layer = viz_state.layers[0]
    assert layer.layerType == 'data'
    assert layer.splitAccessor is None
    assert layer.splitAccessors is not None
    assert len(layer.splitAccessors) == 2


def test_xy_breakdown_and_breakdown_by_mutual_exclusivity() -> None:
    """Test that breakdown and breakdown_by cannot both be specified."""
    with pytest.raises(ValidationError, match="Cannot specify both 'breakdown' and 'breakdown_by'"):
        LensBarChart(
            type='bar',
            data_view='logs-*',
            metrics=[{'aggregation': 'count'}],
            breakdown={'field': 'service.name', 'type': 'values'},
            breakdown_by=[{'field': 'host.name', 'type': 'values'}],
        )


def test_esql_xy_breakdown_by() -> None:
    """Test ESQL XY chart with breakdown_by."""
    config = ESQLBarChart(
        type='bar',
        metrics=[{'field': 'count'}],
        breakdown_by=[{'field': 'service.name'}, {'field': 'host.name'}],
    )

    assert config.breakdown_by is not None
    assert len(config.breakdown_by) == 2


def test_esql_xy_breakdown_mutual_exclusivity() -> None:
    """Test ESQL XY chart breakdown and breakdown_by mutual exclusivity."""
    with pytest.raises(ValidationError, match="Cannot specify both 'breakdown' and 'breakdown_by'"):
        ESQLBarChart(
            type='bar',
            metrics=[{'field': 'count'}],
            breakdown={'field': 'service.name'},
            breakdown_by=[{'field': 'host.name'}],
        )
