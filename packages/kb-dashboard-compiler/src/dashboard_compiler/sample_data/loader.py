"""Sample data loader for Elasticsearch."""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from elastic_transport import TransportError
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from dashboard_compiler.sample_data.config import SampleData
from dashboard_compiler.sample_data.timestamps import transform_documents

logger = logging.getLogger(__name__)


@dataclass
class SampleDataLoadResult:
    """Result of loading sample data into Elasticsearch."""

    success_count: int
    """Number of successfully indexed documents."""

    errors: list[str]
    """List of error messages."""

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
        # model_validator ensures documents is not None when source is 'inline'
        assert sample_data.documents is not None  # noqa: S101
        return sample_data.documents

    if sample_data.source == 'file':
        # model_validator ensures file_path is not None when source is 'file'
        assert sample_data.file_path is not None  # noqa: S101
        file_path = sample_data.file_path
        if base_path is not None and not file_path.is_absolute():
            file_path = base_path / file_path

        if not file_path.exists():
            msg = f'Sample data file not found: {file_path}'
            raise ValueError(msg)

        return _read_ndjson(file_path)

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
    with file_path.open('r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if len(line) > 0:
                documents.append(json.loads(line))  # pyright: ignore[reportAny]
    return documents


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

        actions = [{'_index': index_name, '_source': doc, 'pipeline': '_none'} for doc in transformed_docs]

        success_count, failed_items = await async_bulk(
            es_client,
            actions,
            raise_on_error=False,
        )

        error_messages = []
        if isinstance(failed_items, list) and len(failed_items) > 0:
            for item in failed_items:  # pyright: ignore[reportAny]
                if isinstance(item, dict):
                    # Extract error details from failed item
                    error_info = item.get('index', {}).get('error', {})  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                    if isinstance(error_info, dict):
                        error_type = error_info.get('type', 'unknown')  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                        error_reason = error_info.get('reason', 'unknown reason')  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                        error_messages.append(f'{error_type}: {error_reason}')  # pyright: ignore[reportUnknownMemberType]
                    else:
                        error_messages.append(str(item))  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
                else:
                    error_messages.append(str(item))  # pyright: ignore[reportAny, reportUnknownMemberType]
        elif isinstance(failed_items, int) and failed_items > 0:
            # Fallback for when we get a count instead of items
            error_messages.append(f'{failed_items} document(s) failed to index')  # pyright: ignore[reportUnknownMemberType]

        return SampleDataLoadResult(success_count, error_messages)  # pyright: ignore[reportUnknownArgumentType]

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
