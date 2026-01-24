"""Sample data module for bundling data with dashboards."""

from kb_dashboard.core.sample_data.config import SampleData, TimestampTransform
from kb_dashboard.core.sample_data.timestamps import find_max_timestamp, transform_documents

__all__ = [
    'SampleData',
    'TimestampTransform',
    'find_max_timestamp',
    'transform_documents',
]
