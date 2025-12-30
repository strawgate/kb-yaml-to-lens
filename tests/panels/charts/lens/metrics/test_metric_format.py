"""Unit tests for metric format compilation."""

from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric_format
from dashboard_compiler.panels.charts.lens.metrics.config import LensCustomMetricFormat, LensMetricFormat


def test_compile_lens_metric_format_number() -> None:
    """Test compilation of number format."""
    fmt = LensMetricFormat(type='number')
    result = compile_lens_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'number',
            'params': {
                'decimals': 2,
            },
        }
    )


def test_compile_lens_metric_format_bytes() -> None:
    """Test compilation of bytes format."""
    fmt = LensMetricFormat(type='bytes')
    result = compile_lens_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'bytes',
            'params': {
                'decimals': 2,
            },
        }
    )


def test_compile_lens_metric_format_bits() -> None:
    """Test compilation of bits format."""
    fmt = LensMetricFormat(type='bits')
    result = compile_lens_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'bits',
            'params': {
                'decimals': 0,
            },
        }
    )


def test_compile_lens_metric_format_percent() -> None:
    """Test compilation of percent format."""
    fmt = LensMetricFormat(type='percent')
    result = compile_lens_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'percent',
            'params': {
                'decimals': 2,
            },
        }
    )


def test_compile_lens_metric_format_duration() -> None:
    """Test compilation of duration format."""
    fmt = LensMetricFormat(type='duration')
    result = compile_lens_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'duration',
            'params': {
                'decimals': 0,
            },
        }
    )


def test_compile_lens_metric_format_with_suffix() -> None:
    """Test compilation of format with suffix."""
    fmt = LensMetricFormat(type='number', suffix='KB')
    result = compile_lens_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'number',
            'params': {
                'decimals': 2,
                'suffix': 'KB',
            },
        }
    )


def test_compile_lens_metric_format_with_compact() -> None:
    """Test compilation of format with compact option."""
    fmt = LensMetricFormat(type='number', compact=True)
    result = compile_lens_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'number',
            'params': {
                'decimals': 2,
                'compact': True,
            },
        }
    )


def test_compile_lens_metric_format_with_suffix_and_compact() -> None:
    """Test compilation of format with both suffix and compact."""
    fmt = LensMetricFormat(type='bytes', suffix='MB', compact=True)
    result = compile_lens_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'bytes',
            'params': {
                'decimals': 2,
                'suffix': 'MB',
                'compact': True,
            },
        }
    )


def test_compile_lens_custom_metric_format() -> None:
    """Test compilation of custom metric format."""
    fmt = LensCustomMetricFormat(pattern='0,0.[0000]')
    result = compile_lens_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'custom',
            'params': {
                'decimals': 0,
                'pattern': '0,0.[0000]',
            },
        }
    )


def test_compile_lens_custom_metric_format_with_different_pattern() -> None:
    """Test compilation of custom metric format with different pattern."""
    fmt = LensCustomMetricFormat(pattern='0.00%')
    result = compile_lens_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'custom',
            'params': {
                'decimals': 0,
                'pattern': '0.00%',
            },
        }
    )
