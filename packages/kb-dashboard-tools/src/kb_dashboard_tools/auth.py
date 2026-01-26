"""Authentication and credential handling utilities for Kibana operations."""

from urllib.parse import urlsplit, urlunsplit

__all__ = ['normalize_credentials', 'redact_url']


def normalize_credentials(value: str | None) -> str | None:
    """Normalize an optional credential string, converting empty strings to None.

    This is useful for handling user input where empty strings should be treated
    as missing credentials rather than invalid credentials.

    Args:
        value: The credential string to normalize (e.g., username, password, API key)

    Returns:
        The credential string if non-empty, otherwise None

    Examples:
        >>> normalize_credentials('my-api-key')
        'my-api-key'
        >>> normalize_credentials('')
        None
        >>> normalize_credentials(None)
        None
    """
    if value is None:
        return None
    return value if len(value) > 0 else None


def redact_url(url: str) -> str:
    """Redact credentials from a URL for safe logging.

    Removes any username/password from the URL authority while preserving
    the rest of the URL structure. This is useful for logging URLs without
    exposing sensitive credentials.

    Args:
        url: The URL to redact (may contain credentials in the authority section)

    Returns:
        The URL with credentials removed from the authority

    Examples:
        >>> redact_url('https://user:pass@example.com:9200/path?q=1')
        'https://example.com:9200/path?q=1'
        >>> redact_url('http://localhost:5601/app/kibana')
        'http://localhost:5601/app/kibana'
    """
    parts = urlsplit(url)
    # Strip userinfo from netloc while preserving host format (including IPv6 brackets)
    netloc = parts.netloc
    if '@' in netloc:
        netloc = netloc.split('@', 1)[1]
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))
