"""CLI entry point for the MCP server."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Literal

import rich_click as click

from kb_dashboard_mcp import __version__
from kb_dashboard_mcp.server import build_mcp_server
from kb_dashboard_tools.kibana_client import KibanaClient


@dataclass
class ServerConfig:
    """Configuration for the MCP server."""

    kibana_url: str
    api_key: str | None
    username: str | None
    password: str | None
    verify_ssl: bool
    transport: Literal['stdio', 'sse']


def build_kibana_client(config: ServerConfig) -> KibanaClient:
    """Build a KibanaClient with the given configuration."""
    return KibanaClient(
        url=config.kibana_url,
        api_key=config.api_key,
        username=config.username,
        password=config.password,
        ssl_verify=config.verify_ssl,
    )


async def run_server(config: ServerConfig) -> None:
    """Run the MCP server."""
    client = build_kibana_client(config)

    mcp = await build_mcp_server(client)

    try:
        await mcp.run_async(transport=config.transport)
    finally:
        await client.close()


@click.command()
@click.version_option(version=__version__)
@click.option(
    '--kibana-url',
    envvar='KIBANA_URL',
    required=True,
    help='Kibana server URL (e.g., https://kibana.example.com:5601)',
)
@click.option(
    '--api-key',
    envvar='KIBANA_API_KEY',
    default=None,
    help='API key for Kibana authentication',
)
@click.option(
    '--username',
    envvar='KIBANA_USERNAME',
    default=None,
    help='Username for basic authentication',
)
@click.option(
    '--password',
    envvar='KIBANA_PASSWORD',
    default=None,
    help='Password for basic authentication',
)
@click.option(
    '--no-ssl-verify',
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
    kibana_url: str,
    api_key: str | None,
    username: str | None,
    password: str | None,
    no_ssl_verify: bool,
    transport: str,
) -> None:
    """MCP server for Kibana dashboard building with Elasticsearch data exploration.

    Connects to Kibana and proxies Elasticsearch requests through Kibana's
    /api/console/proxy endpoint.
    """
    if api_key is None and (username is None or password is None):
        msg = 'Either --api-key or both --username and --password must be provided'
        raise click.ClickException(msg)

    config = ServerConfig(
        kibana_url=kibana_url,
        api_key=api_key,
        username=username,
        password=password,
        verify_ssl=not no_ssl_verify,
        transport=transport,  # pyright: ignore[reportArgumentType]
    )

    asyncio.run(run_server(config))


if __name__ == '__main__':
    cli()
