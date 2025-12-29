"""Tests for VSCode extension fixture files."""

from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.dashboard_compiler import load, render

fixture_basedir = Path(__file__).parent.parent.parent / 'vscode-extension' / 'test' / 'fixtures'


def deterministic_id_generator():
    """Generate deterministic UUIDs for testing."""
    i = 0
    while True:
        yield f'00000000-0000-0000-0000-{i:012d}'
        i += 1


@contextmanager
def patch_random_id_generators():
    """Patch all random_id_generator calls with deterministic values."""
    gen = deterministic_id_generator()
    with (
        patch('dashboard_compiler.panels.charts.metric.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.pie.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.xy.compile.random_id_generator', side_effect=lambda: next(gen)),
        patch('dashboard_compiler.panels.charts.esql.columns.compile.random_id_generator', side_effect=lambda: next(gen)),
    ):
        yield


def test_simple_dashboard_fixture_is_valid() -> None:
    """Ensure simple-dashboard.yaml fixture is actually valid and compiles successfully."""
    fixture_path = fixture_basedir / 'simple-dashboard.yaml'
    dashboards = load(str(fixture_path))

    assert len(dashboards) == 1, 'simple-dashboard.yaml should contain exactly one dashboard'

    dashboard = dashboards[0]
    assert isinstance(dashboard, Dashboard)
    assert dashboard.name == 'Simple Test Dashboard'
    assert len(dashboard.panels) == 2

    # Verify it compiles without errors
    with patch_random_id_generators():
        kbn_dashboard = render(dashboard)

    assert kbn_dashboard is not None
    assert kbn_dashboard.attributes.title == 'Simple Test Dashboard'


def test_multi_dashboard_fixture_is_valid() -> None:
    """Ensure multi-dashboard.yaml fixture is actually valid and compiles successfully."""
    fixture_path = fixture_basedir / 'multi-dashboard.yaml'
    dashboards = load(str(fixture_path))

    assert len(dashboards) == 2, 'multi-dashboard.yaml should contain exactly two dashboards'

    # Verify first dashboard
    dashboard1 = dashboards[0]
    assert isinstance(dashboard1, Dashboard)
    assert dashboard1.name == 'First Dashboard'
    assert len(dashboard1.panels) == 1

    # Verify it compiles without errors
    with patch_random_id_generators():
        kbn_dashboard1 = render(dashboard1)

    assert kbn_dashboard1 is not None
    assert kbn_dashboard1.attributes.title == 'First Dashboard'

    # Verify second dashboard
    dashboard2 = dashboards[1]
    assert isinstance(dashboard2, Dashboard)
    assert dashboard2.name == 'Second Dashboard'
    assert len(dashboard2.panels) == 1

    # Verify it compiles without errors
    with patch_random_id_generators():
        kbn_dashboard2 = render(dashboard2)

    assert kbn_dashboard2 is not None
    assert kbn_dashboard2.attributes.title == 'Second Dashboard'


def test_invalid_dashboard_fixture_is_invalid() -> None:
    """Ensure invalid-dashboard.yaml fixture is actually invalid and fails validation."""
    fixture_path = fixture_basedir / 'invalid-dashboard.yaml'

    # Should raise a validation error when loading
    with pytest.raises(ValidationError):
        load(str(fixture_path))
