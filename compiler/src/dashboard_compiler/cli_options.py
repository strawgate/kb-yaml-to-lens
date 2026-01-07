"""Reusable Click option decorators for CLI commands."""

import functools
from collections.abc import Callable
from typing import Any

import rich_click as click

from dashboard_compiler.kibana_client import KibanaClient


def kibana_options[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Add all Kibana connection and authentication options to a Click command.

    This decorator adds the following options:
    - --kibana-url: Kibana base URL (env: KIBANA_URL)
    - --kibana-username: Basic auth username (env: KIBANA_USERNAME)
    - --kibana-password: Basic auth password (env: KIBANA_PASSWORD)
    - --kibana-api-key: API key authentication (env: KIBANA_API_KEY)
    - --kibana-space-id: Kibana space ID (env: KIBANA_SPACE_ID)
    - --kibana-no-ssl-verify: Disable SSL verification

    The decorator automatically:
    - Validates authentication options
    - Creates a KibanaClient with the provided configuration
    - Populates the Click context with the client
    - Removes Kibana parameters from the function signature

    Usage:
        @cli.command()
        @kibana_options
        @click.pass_context
        def my_command(ctx: click.Context) -> None:
            # Access the pre-configured client from context
            from dashboard_compiler.cli_context import CliContext
            if not isinstance(ctx.obj, CliContext):
                raise TypeError("Context object must be CliContext")
            client = ctx.obj.kibana_client
            if client is None:
                raise ValueError("Kibana client not configured")

    Args:
        func: The Click command function to decorate

    Returns:
        The decorated function with Kibana options added and client injection

    """

    @click.option(
        '--kibana-url',
        type=str,
        envvar='KIBANA_URL',
        default='http://localhost:5601',
        help='Kibana base URL. Example: https://kibana.example.com (env: KIBANA_URL)',
    )
    @click.option(
        '--kibana-username',
        type=str,
        envvar='KIBANA_USERNAME',
        help=(
            'Kibana username for basic authentication. Must be used with --kibana-password. '
            'Mutually exclusive with --kibana-api-key. (env: KIBANA_USERNAME)'
        ),
    )
    @click.option(
        '--kibana-password',
        type=str,
        envvar='KIBANA_PASSWORD',
        help=(
            'Kibana password for basic authentication. Must be used with --kibana-username. '
            'Mutually exclusive with --kibana-api-key. (env: KIBANA_PASSWORD)'
        ),
    )
    @click.option(
        '--kibana-api-key',
        type=str,
        envvar='KIBANA_API_KEY',
        help=(
            'Kibana API key for authentication (recommended for production). '
            'Mutually exclusive with --kibana-username/--kibana-password. (env: KIBANA_API_KEY)'
        ),
    )
    @click.option(
        '--kibana-space-id',
        type=str,
        envvar='KIBANA_SPACE_ID',
        help='Kibana space ID to upload dashboards to. If not specified, uses the default space. (env: KIBANA_SPACE_ID)',
    )
    @click.option(
        '--kibana-no-ssl-verify',
        is_flag=True,
        help='Disable SSL certificate verification (useful for self-signed certificates in local development).',
    )
    @click.pass_context
    @functools.wraps(func)
    def wrapper(  # noqa: PLR0913
        ctx: click.Context,
        kibana_url: str,
        kibana_username: str | None,
        kibana_password: str | None,
        kibana_api_key: str | None,
        kibana_space_id: str | None,
        kibana_no_ssl_verify: bool,
        *args: Any,  # pyright: ignore[reportAny]
        **kwargs: Any,  # pyright: ignore[reportAny]
    ) -> R:
        # Validate authentication
        validate_kibana_auth(kibana_api_key, kibana_username, kibana_password)

        # Create and populate context with Kibana client
        from dashboard_compiler.cli_context import CliContext

        if not isinstance(ctx.obj, CliContext):  # pyright: ignore[reportAny]
            msg = 'Context object must be CliContext'
            raise TypeError(msg)

        ctx.obj.kibana_client = KibanaClient(
            url=kibana_url,
            username=kibana_username,
            password=kibana_password,
            api_key=kibana_api_key,
            space_id=kibana_space_id,
            ssl_verify=not kibana_no_ssl_verify,
        )

        # Call the original function without Kibana parameters
        # Note: ctx is passed through because the decorated function has @click.pass_context
        return func(ctx, *args, **kwargs)  # type: ignore[return-value,call-arg]  # pyright: ignore[reportCallIssue,reportUnknownVariableType]

    return wrapper  # type: ignore[return-value]


def elasticsearch_options[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Add all Elasticsearch connection and authentication options to a Click command.

    This decorator adds the following options:
    - --es-url: Elasticsearch base URL (env: ELASTICSEARCH_URL)
    - --es-username: Basic auth username (env: ELASTICSEARCH_USERNAME)
    - --es-password: Basic auth password (env: ELASTICSEARCH_PASSWORD)
    - --es-api-key: API key authentication (env: ELASTICSEARCH_API_KEY)
    - --es-no-ssl-verify: Disable SSL verification

    The decorator automatically:
    - Validates authentication options
    - Creates an AsyncElasticsearch client with the provided configuration
    - Populates the Click context with the client
    - Removes Elasticsearch parameters from the function signature

    Usage:
        @cli.command()
        @elasticsearch_options
        @click.pass_context
        def my_command(ctx: click.Context) -> None:
            # Access the pre-configured client from context
            from dashboard_compiler.cli_context import CliContext
            if not isinstance(ctx.obj, CliContext):
                raise TypeError("Context object must be CliContext")
            client = ctx.obj.es_client
            if client is None:
                raise ValueError("Elasticsearch client not configured")

    Args:
        func: The Click command function to decorate

    Returns:
        The decorated function with Elasticsearch options added and client injection

    """

    @click.option(
        '--es-url',
        type=str,
        envvar='ELASTICSEARCH_URL',
        default='http://localhost:9200',
        help='Elasticsearch base URL. Example: https://elasticsearch.example.com (env: ELASTICSEARCH_URL)',
    )
    @click.option(
        '--es-username',
        type=str,
        envvar='ELASTICSEARCH_USERNAME',
        help='Elasticsearch username for basic authentication (env: ELASTICSEARCH_USERNAME)',
    )
    @click.option(
        '--es-password',
        type=str,
        envvar='ELASTICSEARCH_PASSWORD',
        help='Elasticsearch password for basic authentication (env: ELASTICSEARCH_PASSWORD)',
    )
    @click.option(
        '--es-api-key',
        type=str,
        envvar='ELASTICSEARCH_API_KEY',
        help='Elasticsearch API key for authentication (env: ELASTICSEARCH_API_KEY)',
    )
    @click.option(
        '--es-no-ssl-verify',
        is_flag=True,
        help='Disable SSL certificate verification for Elasticsearch connections.',
    )
    @click.pass_context
    @functools.wraps(func)
    def wrapper(  # noqa: PLR0913
        ctx: click.Context,
        es_url: str,
        es_username: str | None,
        es_password: str | None,
        es_api_key: str | None,
        es_no_ssl_verify: bool,
        *args: Any,  # pyright: ignore[reportAny]
        **kwargs: Any,  # pyright: ignore[reportAny]
    ) -> R:
        # Validate authentication
        validate_elasticsearch_auth(es_api_key, es_username, es_password)

        # Create and populate context with Elasticsearch client
        from elasticsearch import AsyncElasticsearch

        from dashboard_compiler.cli_context import CliContext

        if not isinstance(ctx.obj, CliContext):  # pyright: ignore[reportAny]
            msg = 'Context object must be CliContext'
            raise TypeError(msg)

        # API key takes priority
        if es_api_key is not None:
            ctx.obj.es_client = AsyncElasticsearch(es_url, api_key=es_api_key, verify_certs=not es_no_ssl_verify)
        # Basic auth
        elif es_username is not None and es_password is not None:
            ctx.obj.es_client = AsyncElasticsearch(
                es_url,
                basic_auth=(es_username, es_password),
                verify_certs=not es_no_ssl_verify,
            )
        # No auth
        else:
            ctx.obj.es_client = AsyncElasticsearch(es_url, verify_certs=not es_no_ssl_verify)

        # Call the original function without Elasticsearch parameters
        # Note: ctx is passed through because the decorated function has @click.pass_context
        return func(ctx, *args, **kwargs)  # type: ignore[return-value,call-arg]  # pyright: ignore[reportCallIssue,reportUnknownVariableType]

    return wrapper  # type: ignore[return-value]


def validate_kibana_auth(
    api_key: str | None,
    username: str | None,
    password: str | None,
) -> None:
    """Validate Kibana authentication options.

    Ensures that:
    - API key is not used together with username/password
    - Username and password are used together (not one without the other)

    Args:
        api_key: Kibana API key
        username: Kibana username
        password: Kibana password

    Raises:
        click.UsageError: If authentication options are invalid

    """
    if api_key is not None and (username is not None or password is not None):
        msg = 'Cannot use --kibana-api-key together with --kibana-username or --kibana-password. Choose one authentication method.'
        raise click.UsageError(msg)

    if (username is not None and password is None) or (password is not None and username is None):
        msg = '--kibana-username and --kibana-password must be used together for basic authentication.'
        raise click.UsageError(msg)


def validate_elasticsearch_auth(
    api_key: str | None,
    username: str | None,
    password: str | None,
) -> None:
    """Validate Elasticsearch authentication options.

    Ensures that:
    - API key is not used together with username/password
    - Username and password are used together (not one without the other)

    Args:
        api_key: Elasticsearch API key
        username: Elasticsearch username
        password: Elasticsearch password

    Raises:
        click.UsageError: If authentication options are invalid

    """
    if api_key is not None and (username is not None or password is not None):
        msg = 'Cannot use --es-api-key together with --es-username or --es-password. Choose one authentication method.'
        raise click.UsageError(msg)

    if (username is not None and password is None) or (password is not None and username is None):
        msg = '--es-username and --es-password must be used together for basic authentication.'
        raise click.UsageError(msg)
