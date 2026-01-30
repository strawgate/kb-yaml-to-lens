"""Sample data configuration models for bundling data with dashboards."""

from pathlib import Path
from typing import Any, Literal

from pydantic import Field, model_validator

from kb_dashboard_core.shared.config import BaseCfgModel


class TimestampTransform(BaseCfgModel):
    """Configuration for timestamp transformation in sample data."""

    field: str = Field(default='@timestamp')
    """Name of the timestamp field to transform."""

    enabled: bool = Field(default=True)
    """Whether to apply timestamp transformation.

    When enabled, shifts all timestamps so the maximum becomes 'now'.
    """


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

    timestamp_transform: TimestampTransform | None = Field(default_factory=TimestampTransform)
    """Timestamp transformation configuration. Enabled by default to shift max timestamp to 'now'."""

    create_index_template: bool = Field(default=False)
    """Whether to create an index template for sample data."""

    index_template: dict[str, Any] | None = Field(default=None)
    """Index template configuration (mappings, settings)."""

    @model_validator(mode='after')
    def validate_source_fields(self) -> 'SampleData':
        """Validate that source-specific fields are provided."""
        if self.source == 'inline' and self.documents is None:
            msg = 'documents is required when source is inline'
            raise ValueError(msg)
        if self.source == 'file' and self.file_path is None:
            msg = 'file_path is required when source is file'
            raise ValueError(msg)
        return self
