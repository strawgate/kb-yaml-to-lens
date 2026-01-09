"""Pytest fixtures for integration tests with Elasticsearch and Kibana.

Uses pytest-docker to manage Docker Compose services.
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch

from dashboard_compiler.kibana_client import KibanaClient

logger = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def docker_compose_file() -> Path:
    """Return the path to the docker-compose.yml for integration tests."""
    return Path(__file__).parent / 'docker-compose.yml'


@pytest.fixture(scope='session')
def docker_compose_project_name() -> str:
    """Return a unique project name to avoid conflicts."""
    return 'kb-yaml-integration-tests'


def is_elasticsearch_responsive(url: str) -> bool:
    """Check if Elasticsearch is responsive."""
    try:
        return asyncio.run(_check_es(url))
    except Exception:
        return False


async def _check_es(url: str) -> bool:
    """Async check for Elasticsearch health."""
    async with aiohttp.ClientSession() as session, session.get(f'{url}/_cluster/health') as response:
        if response.status == 200:
            data = await response.json()
            return data.get('status') in ('green', 'yellow')
    return False


def is_kibana_responsive(url: str) -> bool:
    """Check if Kibana is responsive."""
    try:
        return asyncio.run(_check_kibana(url))
    except Exception:
        return False


async def _check_kibana(url: str) -> bool:
    """Async check for Kibana status."""
    async with aiohttp.ClientSession() as session, session.get(f'{url}/api/status') as response:
        if response.status == 200:
            data = await response.json()
            overall = data.get('status', {}).get('overall', {})
            return overall.get('level') == 'available'
    return False


@pytest.fixture(scope='session')
def elasticsearch_url(docker_ip: str, docker_services: Any) -> str:
    """Return Elasticsearch URL after ensuring it's responsive.

    Args:
        docker_ip: IP address of Docker host
        docker_services: pytest-docker services fixture

    Returns:
        Elasticsearch URL

    """
    port = docker_services.port_for('elasticsearch', 9200)
    url = f'http://{docker_ip}:{port}'

    docker_services.wait_until_responsive(
        timeout=120.0,
        pause=2.0,
        check=lambda: is_elasticsearch_responsive(url),
    )
    return url


@pytest.fixture(scope='session')
def kibana_url(docker_ip: str, docker_services: Any, elasticsearch_url: str) -> str:
    """Return Kibana URL after ensuring it's responsive.

    Depends on elasticsearch_url fixture to ensure ES is up before checking Kibana.

    Args:
        docker_ip: IP address of Docker host
        docker_services: pytest-docker services fixture
        elasticsearch_url: Elasticsearch URL (fixture dependency - ensures ES is up first)

    Returns:
        Kibana URL

    """
    _ = elasticsearch_url  # Ensure ES is up before checking Kibana
    port = docker_services.port_for('kibana', 5601)
    url = f'http://{docker_ip}:{port}'

    docker_services.wait_until_responsive(
        timeout=180.0,
        pause=3.0,
        check=lambda: is_kibana_responsive(url),
    )
    return url


@pytest.fixture
async def es_client(elasticsearch_url: str) -> AsyncGenerator[AsyncElasticsearch]:
    """Create an async Elasticsearch client.

    Args:
        elasticsearch_url: Elasticsearch URL

    Yields:
        AsyncElasticsearch client

    """
    client = AsyncElasticsearch(hosts=[elasticsearch_url])
    try:
        yield client
    finally:
        await client.close()


@pytest.fixture
async def kibana_client(kibana_url: str) -> AsyncGenerator[KibanaClient]:
    """Create a Kibana client.

    Args:
        kibana_url: Kibana URL

    Yields:
        KibanaClient instance

    """
    client = KibanaClient(url=kibana_url)
    try:
        yield client
    finally:
        await client.close()


@pytest.fixture(scope='session')
def sample_logs_data() -> list[dict[str, Any]]:
    """Generate sample log documents for testing."""
    import datetime

    base_time = datetime.datetime.now(tz=datetime.UTC)
    documents = []

    log_levels = ['info', 'warn', 'error', 'debug']
    hosts = ['host-1', 'host-2', 'host-3']
    tags = ['web', 'api', 'database', 'cache', 'auth']

    for i in range(100):
        doc = {
            '@timestamp': (base_time - datetime.timedelta(minutes=i)).isoformat(),
            'log': {
                'level': log_levels[i % len(log_levels)],
            },
            'host': {
                'name': hosts[i % len(hosts)],
            },
            'tags': [tags[i % len(tags)], tags[(i + 1) % len(tags)]],
            'message': f'Sample log message {i}',
        }
        documents.append(doc)

    return documents


@pytest.fixture
async def loaded_sample_data(
    es_client: AsyncElasticsearch,
    sample_logs_data: list[dict[str, Any]],
) -> AsyncGenerator[str]:
    """Load sample data into Elasticsearch and return the index name.

    Args:
        es_client: Elasticsearch client
        sample_logs_data: Sample log documents

    Yields:
        Index name containing the sample data

    """
    from elasticsearch.helpers import async_bulk

    index_name = 'logs-sample'

    # Create index with appropriate mappings
    mapping = {
        'mappings': {
            'properties': {
                '@timestamp': {'type': 'date'},
                'log': {
                    'properties': {
                        'level': {'type': 'keyword'},
                    },
                },
                'host': {
                    'properties': {
                        'name': {'type': 'keyword'},
                    },
                },
                'tags': {'type': 'keyword'},
                'message': {'type': 'text'},
            },
        },
    }

    # Delete index if exists
    if await es_client.indices.exists(index=index_name):
        await es_client.indices.delete(index=index_name)

    # Create index
    await es_client.indices.create(index=index_name, body=mapping)

    # Bulk index documents
    actions = [{'_index': index_name, '_source': doc} for doc in sample_logs_data]
    await async_bulk(es_client, actions)

    # Refresh to make documents searchable
    await es_client.indices.refresh(index=index_name)

    yield index_name

    # Cleanup
    await es_client.indices.delete(index=index_name, ignore_unavailable=True)


@pytest.fixture
async def data_view(kibana_client: KibanaClient, loaded_sample_data: str) -> AsyncGenerator[str]:
    """Create a Kibana data view for the sample data.

    Args:
        kibana_client: Kibana client
        loaded_sample_data: Index name

    Yields:
        Data view ID

    """
    data_view_id = 'logs-sample-view'
    index_pattern = f'{loaded_sample_data}*'

    # Create data view via Kibana API
    try:
        await kibana_client.create_data_view(data_view_id, index_pattern)
        logger.info(f'Created data view: {data_view_id}')
    except Exception as e:
        logger.warning(f'Failed to create data view: {e}')

    yield data_view_id

    # Cleanup - delete data view
    try:
        session = kibana_client._get_session()
        async with session.delete(
            f'{kibana_client.url}/api/data_views/data_view/{data_view_id}',
            headers={'kbn-xsrf': 'true'},
        ) as response:
            if response.status == 200:
                logger.info(f'Deleted data view: {data_view_id}')
    except Exception as e:
        logger.warning(f'Failed to delete data view: {e}')


async def get_dashboard_panel_errors(kibana_client: KibanaClient, dashboard_id: str) -> list[dict[str, Any]]:
    """Fetch dashboard and check for panel rendering errors.

    This uses the Kibana API to get dashboard metadata and check for issues.

    Args:
        kibana_client: Kibana client
        dashboard_id: Dashboard ID to check

    Returns:
        List of panel errors found

    """
    errors: list[dict[str, Any]] = []

    # Export the dashboard to verify structure
    try:
        ndjson = await kibana_client.export_dashboard(dashboard_id)

        # Parse each line of NDJSON
        for line in ndjson.strip().split('\n'):
            if not line:
                continue
            obj = json.loads(line)

            # Check for error markers in saved objects
            if 'error' in obj:
                errors.append(
                    {
                        'type': 'export_error',
                        'id': obj.get('id'),
                        'error': obj['error'],
                    }
                )

            # Check panel configurations for issues
            if obj.get('type') == 'dashboard':
                panels_json = obj.get('attributes', {}).get('panelsJSON')
                if panels_json:
                    panels = json.loads(panels_json) if isinstance(panels_json, str) else panels_json
                    for panel in panels:
                        # Check for missing embeddable config
                        if 'embeddableConfig' not in panel:
                            errors.append(
                                {
                                    'type': 'missing_embeddable_config',
                                    'panel_id': panel.get('panelIndex'),
                                    'panel_type': panel.get('type'),
                                }
                            )

                        # Check for lens-specific errors
                        if panel.get('type') == 'lens':
                            config = panel.get('embeddableConfig', {})
                            attrs = config.get('attributes', {})
                            state = attrs.get('state', {})

                            # Check for missing visualization state
                            if 'visualization' not in state:
                                errors.append(
                                    {
                                        'type': 'missing_visualization_state',
                                        'panel_id': panel.get('panelIndex'),
                                        'title': attrs.get('title'),
                                    }
                                )

                            # Check for missing datasource state
                            if 'datasourceStates' not in state:
                                errors.append(
                                    {
                                        'type': 'missing_datasource_state',
                                        'panel_id': panel.get('panelIndex'),
                                        'title': attrs.get('title'),
                                    }
                                )

    except Exception as e:
        errors.append(
            {
                'type': 'api_error',
                'error': str(e),
            }
        )

    return errors
