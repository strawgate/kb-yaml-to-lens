"""Unit tests for ES|QL metric format compilation."""

from inline_snapshot import snapshot

from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_metric_format
from dashboard_compiler.panels.charts.esql.columns.config import ESQLCustomMetricFormat, ESQLMetricFormat


def test_compile_esql_metric_format_number() -> None:
    """Test compilation of number format."""
    fmt = ESQLMetricFormat(type='number')
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'number',
            'params': {
                'decimals': 2,
            },
        }
    )


def test_compile_esql_metric_format_bytes() -> None:
    """Test compilation of bytes format."""
    fmt = ESQLMetricFormat(type='bytes')
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'bytes',
            'params': {
                'decimals': 2,
            },
        }
    )


def test_compile_esql_metric_format_bits() -> None:
    """Test compilation of bits format."""
    fmt = ESQLMetricFormat(type='bits')
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'bits',
            'params': {
                'decimals': 0,
            },
        }
    )


def test_compile_esql_metric_format_percent() -> None:
    """Test compilation of percent format."""
    fmt = ESQLMetricFormat(type='percent')
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'percent',
            'params': {
                'decimals': 2,
            },
        }
    )


def test_compile_esql_metric_format_duration() -> None:
    """Test compilation of duration format."""
    fmt = ESQLMetricFormat(type='duration')
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'duration',
            'params': {
                'decimals': 0,
            },
        }
    )


def test_compile_esql_metric_format_with_suffix() -> None:
    """Test compilation of format with suffix."""
    fmt = ESQLMetricFormat(type='number', suffix='KB')
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'number',
            'params': {
                'decimals': 2,
                'suffix': 'KB',
            },
        }
    )


def test_compile_esql_metric_format_with_compact() -> None:
    """Test compilation of format with compact option."""
    fmt = ESQLMetricFormat(type='number', compact=True)
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'number',
            'params': {
                'decimals': 2,
                'compact': True,
            },
        }
    )


def test_compile_esql_metric_format_with_pattern() -> None:
    """Test compilation of format with pattern."""
    fmt = ESQLMetricFormat(type='bytes', pattern='0,0.0 b')
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'bytes',
            'params': {
                'decimals': 2,
                'pattern': '0,0.0 b',
            },
        }
    )


def test_compile_esql_metric_format_with_suffix_and_compact() -> None:
    """Test compilation of format with both suffix and compact."""
    fmt = ESQLMetricFormat(type='bytes', suffix='MB', compact=True)
    result = compile_esql_metric_format(fmt)

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


def test_compile_esql_metric_format_with_pattern_and_suffix() -> None:
    """Test compilation of format with pattern and suffix."""
    fmt = ESQLMetricFormat(type='number', pattern='0,0.00', suffix='KB')
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'number',
            'params': {
                'decimals': 2,
                'pattern': '0,0.00',
                'suffix': 'KB',
            },
        }
    )


def test_compile_esql_metric_format_with_pattern_and_compact() -> None:
    """Test compilation of format with pattern and compact."""
    fmt = ESQLMetricFormat(type='bytes', pattern='0.0 b', compact=True)
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'bytes',
            'params': {
                'decimals': 2,
                'pattern': '0.0 b',
                'compact': True,
            },
        }
    )


def test_compile_esql_custom_metric_format() -> None:
    """Test compilation of custom metric format."""
    fmt = ESQLCustomMetricFormat(pattern='0,0.[0000]')
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'custom',
            'params': {
                'decimals': 0,
                'pattern': '0,0.[0000]',
            },
        }
    )


def test_compile_esql_custom_metric_format_with_different_pattern() -> None:
    """Test compilation of custom metric format with different pattern."""
    fmt = ESQLCustomMetricFormat(pattern='0.00%')
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'custom',
            'params': {
                'decimals': 0,
                'pattern': '0.00%',
            },
        }
    )


def test_compile_esql_metric_format_with_explicit_decimals() -> None:
    """Test compilation of format with explicit decimals override."""
    fmt = ESQLMetricFormat(type='number', decimals=4)
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'number',
            'params': {
                'decimals': 4,
            },
        }
    )


def test_compile_esql_metric_format_bits_with_explicit_decimals() -> None:
    """Test compilation of bits format with explicit decimals override."""
    fmt = ESQLMetricFormat(type='bits', decimals=2)
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'bits',
            'params': {
                'decimals': 2,
            },
        }
    )


def test_compile_esql_metric_format_with_decimals_and_suffix() -> None:
    """Test compilation of format with both decimals and suffix."""
    fmt = ESQLMetricFormat(type='number', decimals=1, suffix='ms')
    result = compile_esql_metric_format(fmt)

    assert result.model_dump() == snapshot(
        {
            'id': 'number',
            'params': {
                'decimals': 1,
                'suffix': 'ms',
            },
        }
    )
