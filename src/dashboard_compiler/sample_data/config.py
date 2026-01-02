"""Sample data configuration models for bundling data with dashboards."""

from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from dashboard_compiler.shared.config import BaseCfgModel


class TimestampTransform(BaseCfgModel):
    """Configuration for timestamp transformation in sample data."""

    field: str = Field(default='@timestamp')
    """Name of the timestamp field to transform."""

    strategy: Literal['shift', 'now_minus', 'absolute'] = Field(...)
    """Transformation strategy for timestamps."""

    offset: str | None = Field(default=None)
    """Offset for shift strategy (e.g., '24h', '7d', 'now-1w')."""

    range_start: str | None = Field(default=None)
    """Start of time range for now_minus strategy (e.g., 'now-24h')."""

    range_end: str | None = Field(default=None)
    """End of time range for now_minus strategy (e.g., 'now')."""


class SampleData(BaseCfgModel):
    """Sample data configuration for dashboards."""

    source: Literal['inline', 'file'] = Field(...)
    """Whether sample data is inline in YAML or in an external file."""

    index_pattern: str = Field(...)
    """Target index pattern for sample data (e.g., 'logs-*', 'metrics-*')."""

    documents: list[dict[str, Any]] | None = Field(default=None)
    """Inline sample documents (when source='inline')."""

    file_path: Path | None = Field(default=None)
    """Path to NDJSON file with sample data (when source='file')."""

    format: Literal['ndjson', 'json_array'] = Field(default='ndjson')
    """Format of sample data."""

    timestamp_transform: TimestampTransform | None = Field(default=None)
    """Optional timestamp transformation to apply."""

    bypass_pipeline: bool = Field(default=True)
    """Whether to bypass ingest pipeline during data loading."""

    create_index_template: bool = Field(default=False)
    """Whether to create an index template for sample data."""

    index_template: dict[str, Any] | None = Field(default=None)
    """Index template configuration (mappings, settings)."""
