"""Unit tests for shared compilation utility functions, including extract_metrics_from_config."""

import pytest
from dashboard_compiler.shared.compile import extract_metrics_from_config
from typing import Any

class MockConfigWithMetric:
    metric: Any
    metrics: list[Any] | None = None

    def __init__(self, metric: Any):
        self.metric = metric

class MockConfigWithMetrics:
    metric: Any = None
    metrics: list[Any] | None

    def __init__(self, metrics: list[Any]):
        self.metrics = metrics

class MockConfigWithBoth:
    metric: Any
    metrics: list[Any] | None

    def __init__(self, metric: Any, metrics: list[Any]):
        self.metric = metric
        self.metrics = metrics

class MockConfigWithNeither:
    metric: Any = None
    metrics: list[Any] | None = None

class MockConfigWithNone:
    metric: Any = None
    metrics: list[Any] | None = None

def test_extract_metrics_single() -> None:
    """Test extracting a single metric."""
    config = MockConfigWithMetric('metric1')
    assert extract_metrics_from_config(config) == ['metric1']

def test_extract_metrics_multiple() -> None:
    """Test extracting multiple metrics."""
    config = MockConfigWithMetrics(['metric1', 'metric2'])
    assert extract_metrics_from_config(config) == ['metric1', 'metric2']

def test_extract_metrics_both_priority() -> None:
    """Test that single metric takes priority if both are present."""
    config = MockConfigWithBoth('single', ['multi'])
    assert extract_metrics_from_config(config) == ['single']

def test_extract_metrics_neither_raises() -> None:
    """Test that ValueError is raised if neither is present."""
    config = MockConfigWithNeither()
    with pytest.raises(ValueError, match="Either 'metric' or 'metrics' must be provided"):
        extract_metrics_from_config(config)

def test_extract_metrics_none_raises() -> None:
    """Test that ValueError is raised if both are None."""
    config = MockConfigWithNone()
    with pytest.raises(ValueError, match="Either 'metric' or 'metrics' must be provided"):
        extract_metrics_from_config(config)

def test_extract_metrics_empty_list_raises() -> None:
    """Test that ValueError is raised if metrics is an empty list."""
    class MockConfigEmptyMetrics:
        metric: Any = None
        metrics: list[Any] = []

    config = MockConfigEmptyMetrics()
    with pytest.raises(ValueError, match="Either 'metric' or 'metrics' must be provided"):
        extract_metrics_from_config(config)
