"""Utility functions for dashboard compiler."""

import re
import urllib.parse


def extract_dashboard_id_from_url(url_or_id: str) -> str:
    """Extract dashboard ID from Kibana URL or return plain ID as-is.

    This function accepts both Kibana dashboard URLs and plain dashboard IDs.
    For URLs, it extracts the dashboard ID from patterns like:
    - https://kibana.example.com/app/dashboards#/view/{id}
    - https://kibana.example.com/app/dashboards#/view/{id}?_g=...
    - https://kibana.example.com/s/{space}/app/dashboards#/view/{id}

    For plain dashboard IDs, it returns them unchanged.

    Args:
        url_or_id: Either a Kibana dashboard URL or a plain dashboard ID

    Returns:
        The extracted dashboard ID

    Raises:
        ValueError: If the URL format is invalid and doesn't contain a recognizable dashboard ID

    Examples:
        >>> extract_dashboard_id_from_url("abc123")
        'abc123'
        >>> extract_dashboard_id_from_url("https://kibana.example.com/app/dashboards#/view/my-dashboard-id")
        'my-dashboard-id'
        >>> extract_dashboard_id_from_url("https://kibana.example.com/s/myspace/app/dashboards#/view/my-dashboard-id?_g=...")
        'my-dashboard-id'

    """
    # Pattern to match dashboard IDs in Kibana URLs
    # Matches both #/view/{id} and /view/{id} patterns
    # Captures everything after /view/ until the next ? or & or end of string
    pattern = r'(?:#/view/|/view/)([^?&#]+)'

    match = re.search(pattern, url_or_id)
    if match is not None:
        dashboard_id = match.group(1)
        # URL decode any %20 (spaces) or other encoded characters
        return urllib.parse.unquote(dashboard_id)

    # If no URL pattern found, check if it looks like a URL
    # Check for common URL patterns: contains ://, starts with www., or looks like a schemeless domain/path
    looks_like_url = '://' in url_or_id or url_or_id.startswith('www.') or re.match(r'^[^/\s]+\.[^/\s]+/', url_or_id) is not None
    if looks_like_url is True:
        msg = (
            f'Invalid Kibana dashboard URL format: {url_or_id}. '
            'Expected format: https://kibana.example.com/app/dashboards#/view/{{dashboard-id}}'
        )
        raise ValueError(msg)

    # Otherwise, treat it as a plain dashboard ID
    return url_or_id
