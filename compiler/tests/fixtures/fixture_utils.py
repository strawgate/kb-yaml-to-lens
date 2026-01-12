"""Fixture test utilities for comparing compiled output against Kibana fixtures.

This module provides utilities for comparing compiled panel output
against dynamically generated fixtures using DeepDiff.
"""

from __future__ import annotations

from typing import Any

from deepdiff import DeepDiff


def normalize_compiled_panel(compiled_panel: dict[str, Any]) -> dict[str, Any]:
    """Normalize a compiled panel's embeddableConfig for fixture comparison.

    Extracts the embeddableConfig from a compiled panel and normalizes it
    to match the fixture format.

    Args:
        compiled_panel: A panel from the compiled dashboard's panelsJSON.

    Returns:
        Normalized embeddableConfig dictionary.
    """
    config = compiled_panel.get('embeddableConfig', {})
    attributes = config.get('attributes', {})

    return {
        'title': attributes.get('title', compiled_panel.get('title', '')),
        'visualizationType': attributes.get('visualizationType', ''),
        'references': attributes.get('references', []),
        'state': attributes.get('state', {}),
    }


def compare_with_deepdiff(
    compiled: dict[str, Any],
    fixture: dict[str, Any],
) -> DeepDiff:
    """Compare compiled output to fixture using DeepDiff.

    Args:
        compiled: Compiled panel configuration.
        fixture: Generated fixture JSON.

    Returns:
        A DeepDiff object containing the differences.
    """
    return DeepDiff(
        fixture,
        compiled,
        ignore_order=True,
        verbose_level=2,
    )
