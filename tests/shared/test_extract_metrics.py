"""Unit tests for shared compilation utility functions, including extract_metrics_from_config."""

from typing import Any, ClassVar

import pytest

from dashboard_compiler.shared.compile import extract_metrics_from_config


class MockConfigWithMetric:
    """Mock config with a single metric."""

    metric: Any
    metrics: list[Any] | None = None

    def __init__(self, metric: Any) -> None:
        """Initialize with a single metric."""
        self.metric = metric


class MockConfigWithMetrics:
    """Mock config with multiple metrics."""

    metric: Any = None
    metrics: list[Any] | None

    def __init__(self, metrics: list[Any]) -> None:
        """Initialize with multiple metrics."""
        self.metrics = metrics


class MockConfigWithBoth:
    """Mock config with both single and multiple metrics."""

    metric: Any
    metrics: list[Any] | None

    def __init__(self, metric: Any, metrics: list[Any]) -> None:
        """Initialize with both single and multiple metrics."""
        self.metric = metric
        self.metrics = metrics


class MockConfigWithNeither:
    """Mock config with neither metric nor metrics."""

    metric: Any = None
    metrics: list[Any] | None = None


class MockConfigWithNone:
    """Mock config with both set to None."""

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
        extract_metrics_from_config(config)  # pyright: ignore[reportUnusedCallResult]


def test_extract_metrics_none_raises() -> None:
    """Test that ValueError is raised if both are None."""
    config = MockConfigWithNone()
    with pytest.raises(ValueError, match="Either 'metric' or 'metrics' must be provided"):
        extract_metrics_from_config(config)  # pyright: ignore[reportUnusedCallResult]


def test_extract_metrics_empty_list_raises() -> None:
    """Test that ValueError is raised if metrics is an empty list."""

    class MockConfigEmptyMetrics:
        """Mock config with empty metrics list."""

        metric: Any = None
        metrics: ClassVar[list[Any]] = []

    config = MockConfigEmptyMetrics()
    with pytest.raises(ValueError, match="Either 'metric' or 'metrics' must be provided"):
        extract_metrics_from_config(config)  # pyright: ignore[reportUnusedCallResult]
