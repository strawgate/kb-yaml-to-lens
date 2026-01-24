"""CLI entry point for the MCP server."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Literal

import rich_click as click
from elasticsearch import AsyncElasticsearch

from kb_dashboard_mcp import __version__
from kb_dashboard_mcp.server import build_mcp_server


@dataclass
class ServerConfig:
    """Configuration for the MCP server."""

    es_url: str
    api_key: str | None
    username: str | None
    password: str | None
    verify_ssl: bool
    transport: Literal['stdio', 'sse']


def build_es_client(config: ServerConfig) -> AsyncElasticsearch:
    """Build an AsyncElasticsearch client with the given configuration."""
    if config.api_key is not None:
        return AsyncElasticsearch(
            hosts=[config.es_url],
            verify_certs=config.verify_ssl,
            http_compress=True,
            api_key=config.api_key,
        )

    if config.username is not None and config.password is not None:
        return AsyncElasticsearch(
            hosts=[config.es_url],
            verify_certs=config.verify_ssl,
            http_compress=True,
            basic_auth=(config.username, config.password),
        )

    return AsyncElasticsearch(
        hosts=[config.es_url],
        verify_certs=config.verify_ssl,
        http_compress=True,
    )


async def run_server(config: ServerConfig) -> None:
    """Run the MCP server."""
    es = build_es_client(config)

    try:
        await es.ping()
    except Exception as e:
        msg = f'Failed to connect to Elasticsearch: {e}'
        raise click.ClickException(msg) from e

    mcp = await build_mcp_server(es)

    try:
        await mcp.run_async(transport=config.transport)
    finally:
        await es.close()


@click.command()
@click.version_option(version=__version__)
@click.option(
    '--es-url',
    envvar='ES_URL',
    required=True,
    help='Elasticsearch cluster URL',
)
@click.option(
    '--es-api-key',
    envvar='ES_API_KEY',
    default=None,
    help='API key for Elasticsearch authentication',
)
@click.option(
    '--es-username',
    envvar='ES_USERNAME',
    default=None,
    help='Username for basic authentication',
)
@click.option(
    '--es-password',
    envvar='ES_PASSWORD',
    default=None,
    help='Password for basic authentication',
)
@click.option(
    '--es-no-ssl-verify',
    is_flag=True,
    default=False,
    help='Disable SSL certificate verification',
)
@click.option(
    '--transport',
    type=click.Choice(['stdio', 'sse']),
    default='stdio',
    help='Transport protocol for MCP communication',
)
def cli(
    es_url: str,
    es_api_key: str | None,
    es_username: str | None,
    es_password: str | None,
    es_no_ssl_verify: bool,
    transport: str,
) -> None:
    """MCP server for Kibana dashboard building with Elasticsearch data exploration."""
    if es_api_key is None and (es_username is None or es_password is None):
        msg = 'Either --es-api-key or both --es-username and --es-password must be provided'
        raise click.ClickException(msg)

    config = ServerConfig(
        es_url=es_url,
        api_key=es_api_key,
        username=es_username,
        password=es_password,
        verify_ssl=not es_no_ssl_verify,
        transport=transport,  # pyright: ignore[reportArgumentType]
    )

    asyncio.run(run_server(config))


if __name__ == '__main__':
    cli()
