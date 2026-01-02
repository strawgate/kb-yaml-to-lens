"""Sample data loader for Elasticsearch."""

import json
import logging
from pathlib import Path
from typing import Any

from elastic_transport import TransportError
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from dashboard_compiler.sample_data.config import SampleData
from dashboard_compiler.sample_data.timestamps import transform_documents

logger = logging.getLogger(__name__)


class SampleDataLoadResult:
    """Result of loading sample data into Elasticsearch."""

    success_count: int
    errors: list[str]

    def __init__(self, success_count: int, errors: list[str]) -> None:
        """Initialize load result.

        Args:
            success_count: Number of successfully indexed documents
            errors: List of error messages

        """
        self.success_count = success_count
        self.errors = errors

    @property
    def success(self) -> bool:
        """Whether the load was successful."""
        return len(self.errors) == 0


def read_documents(sample_data: SampleData, base_path: Path | None = None) -> list[dict[str, Any]]:
    """Read sample documents from inline or file source.

    Args:
        sample_data: Sample data configuration
        base_path: Base path for resolving relative file paths

    Returns:
        List of document dictionaries

    Raises:
        ValueError: If source is invalid or file cannot be read

    """
    if sample_data.source == 'inline':
        if sample_data.documents is None:
            msg = 'documents field is required when source is inline'
            raise ValueError(msg)
        return sample_data.documents

    if sample_data.source == 'file':
        if sample_data.file_path is None:
            msg = 'file_path field is required when source is file'
            raise ValueError(msg)

        file_path = sample_data.file_path
        if base_path is not None and not file_path.is_absolute():
            file_path = base_path / file_path

        if not file_path.exists():
            msg = f'Sample data file not found: {file_path}'
            raise ValueError(msg)

        if sample_data.format == 'ndjson':
            return _read_ndjson(file_path)
        if sample_data.format == 'json_array':
            return _read_json_array(file_path)

        msg = f'Unsupported format: {sample_data.format}'
        raise ValueError(msg)

    msg = f'Invalid source: {sample_data.source}'
    raise ValueError(msg)


def _read_ndjson(file_path: Path) -> list[dict[str, Any]]:
    """Read NDJSON file.

    Args:
        file_path: Path to NDJSON file

    Returns:
        List of parsed JSON documents

    """
    documents: list[dict[str, Any]] = []
    with file_path.open('r') as f:
        for raw_line in f:
            line = raw_line.strip()
            if len(line) > 0:
                documents.append(json.loads(line))  # pyright: ignore[reportAny]
    return documents


def _read_json_array(file_path: Path) -> list[dict[str, Any]]:
    """Read JSON array file.

    Args:
        file_path: Path to JSON file

    Returns:
        List of parsed JSON documents

    """
    with file_path.open('r') as f:
        data = json.load(f)  # pyright: ignore[reportAny]
        if not isinstance(data, list):
            msg = f'Expected JSON array in {file_path}, got {type(data).__name__}'  # pyright: ignore[reportAny]
            raise TypeError(msg)
        return data  # pyright: ignore[reportUnknownVariableType]


async def load_sample_data(
    es_client: AsyncElasticsearch,
    sample_data: SampleData,
    base_path: Path | None = None,
) -> SampleDataLoadResult:
    """Load sample data into Elasticsearch.

    Args:
        es_client: Async Elasticsearch client
        sample_data: Sample data configuration
        base_path: Base path for resolving relative file paths

    Returns:
        Load result with success count and errors

    """
    try:
        documents = read_documents(sample_data, base_path)
        transformed_docs = transform_documents(documents, sample_data.timestamp_transform)

        index_name = sample_data.index_pattern.replace('*', 'sample')

        if sample_data.create_index_template is True and sample_data.index_template is not None:
            await _create_index_template(es_client, index_name, sample_data.index_template)

        if sample_data.bypass_pipeline is True:
            actions = [{'_index': index_name, '_source': doc, 'pipeline': None} for doc in transformed_docs]
        else:
            actions = [{'_index': index_name, '_source': doc} for doc in transformed_docs]

        success_count, failed_count = await async_bulk(
            es_client,
            actions,
            raise_on_error=False,
        )

        error_messages = [] if failed_count == 0 else [f'{failed_count} document(s) failed to index']
        return SampleDataLoadResult(success_count, error_messages)

    except (ValueError, OSError, json.JSONDecodeError, TransportError) as e:
        return SampleDataLoadResult(0, [str(e)])


async def _create_index_template(
    es_client: AsyncElasticsearch,
    index_name: str,
    template_config: dict[str, Any],
) -> None:
    """Create index template for sample data.

    Args:
        es_client: Async Elasticsearch client
        index_name: Name of the index
        template_config: Template configuration (mappings, settings)

    """
    template_name = f'{index_name}-template'
    _ = await es_client.indices.put_index_template(
        name=template_name,
        index_patterns=[f'{index_name}*'],
        template=template_config,
    )
    logger.info(f'Created index template: {template_name}')
