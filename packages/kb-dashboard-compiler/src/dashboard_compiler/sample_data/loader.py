"""Sample data loader for Elasticsearch via Kibana proxy."""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from dashboard_compiler.sample_data.config import SampleData
from dashboard_compiler.sample_data.timestamps import transform_documents

if TYPE_CHECKING:
    from dashboard_compiler.kibana_client import KibanaClient

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
    kibana_client: 'KibanaClient',
    sample_data: SampleData,
    base_path: Path | None = None,
) -> SampleDataLoadResult:
    """Load sample data into Elasticsearch via Kibana proxy.

    Args:
        kibana_client: Kibana client for proxying requests to Elasticsearch
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
            await _create_index_template(kibana_client, index_name, sample_data.index_template)

        actions = [{'_index': index_name, '_source': doc, 'pipeline': '_none'} for doc in transformed_docs]

        success_count, failed_items = await kibana_client.proxy_bulk(actions)

        error_messages: list[str] = []
        if len(failed_items) > 0:
            for item in failed_items:
                # Extract error details from failed item
                for action_result in item.values():  # pyright: ignore[reportAny]
                    if isinstance(action_result, dict):
                        error_info = action_result.get('error', {})  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                        if isinstance(error_info, dict):
                            error_type = error_info.get('type', 'unknown')  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                            error_reason = error_info.get('reason', 'unknown reason')  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                            error_messages.append(f'{error_type}: {error_reason}')
                        else:
                            error_messages.append(str(action_result))  # pyright: ignore[reportUnknownArgumentType]
                    else:
                        error_messages.append(str(item))

        return SampleDataLoadResult(success_count, error_messages)

    except (ValueError, OSError, json.JSONDecodeError) as e:
        return SampleDataLoadResult(0, [str(e)])


async def _create_index_template(
    kibana_client: 'KibanaClient',
    index_name: str,
    template_config: dict[str, Any],
) -> None:
    """Create index template for sample data via Kibana proxy.

    Args:
        kibana_client: Kibana client for proxying requests to Elasticsearch
        index_name: Name of the index
        template_config: Template configuration (mappings, settings)

    """
    template_name = f'{index_name}-template'
    await kibana_client.proxy_put_index_template(
        name=template_name,
        index_patterns=[f'{index_name}*'],
        template=template_config,
    )
    logger.info(f'Created index template: {template_name}')
