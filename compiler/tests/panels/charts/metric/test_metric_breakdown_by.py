"""Test breakdown_by functionality for metric charts."""

import pytest
from pydantic import ValidationError

from dashboard_compiler.panels.charts.metric.compile import compile_lens_metric_chart
from dashboard_compiler.panels.charts.metric.config import ESQLMetricChart, LensMetricChart


def test_breakdown_by_single_field() -> None:
    """Test metric chart with a single breakdown_by field."""
    config = LensMetricChart(
        type='metric',
        data_view='logs-*',
        primary={'aggregation': 'count'},
        breakdown_by=[{'field': 'service.name', 'type': 'values'}],
    )

    _layer_id, _columns, viz_state = compile_lens_metric_chart(config)

    assert viz_state.breakdownByAccessor is not None


def test_breakdown_by_multiple_fields() -> None:
    """Test metric chart with multiple breakdown_by fields (only first is used)."""
    config = LensMetricChart(
        type='metric',
        data_view='logs-*',
        primary={'aggregation': 'count'},
        breakdown_by=[
            {'field': 'service.name', 'type': 'values'},
            {'field': 'host.name', 'type': 'values'},
        ],
    )

    _layer_id, _columns, viz_state = compile_lens_metric_chart(config)

    # Only the first field is used (Kibana limitation)
    assert viz_state.breakdownByAccessor is not None


def test_breakdown_and_breakdown_by_mutual_exclusivity() -> None:
    """Test that breakdown and breakdown_by cannot both be specified."""
    with pytest.raises(ValidationError, match="Cannot specify both 'breakdown' and 'breakdown_by'"):
        LensMetricChart(
            type='metric',
            data_view='logs-*',
            primary={'aggregation': 'count'},
            breakdown={'field': 'service.name', 'type': 'values'},
            breakdown_by=[{'field': 'host.name', 'type': 'values'}],
        )


def test_esql_breakdown_by() -> None:
    """Test ESQL metric chart with breakdown_by."""
    config = ESQLMetricChart(
        type='metric',
        primary={'field': 'count'},
        breakdown_by=[{'field': 'service.name'}],
    )

    assert config.breakdown_by is not None
    assert len(config.breakdown_by) == 1


def test_esql_breakdown_mutual_exclusivity() -> None:
    """Test ESQL metric chart breakdown and breakdown_by mutual exclusivity."""
    with pytest.raises(ValidationError, match="Cannot specify both 'breakdown' and 'breakdown_by'"):
        ESQLMetricChart(
            type='metric',
            primary={'field': 'count'},
            breakdown={'field': 'service.name'},
            breakdown_by=[{'field': 'host.name'}],
        )
