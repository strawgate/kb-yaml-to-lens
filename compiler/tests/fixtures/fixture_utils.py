"""Utilities for comparing compiler output against generated fixtures.

Simple helpers for normalizing and diffing compiled panels vs Kibana fixtures.
"""

from __future__ import annotations

from typing import Any

from deepdiff import DeepDiff


def normalize_compiled_panel(compiled_panel: dict[str, Any]) -> dict[str, Any]:
    """Extract and normalize embeddableConfig from a compiled panel.

    Extracts the relevant fields to match fixture format.

    Args:
        compiled_panel: Panel from compiled dashboard's panelsJSON

    Returns:
        Normalized embeddableConfig dictionary
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
        compiled: Compiled panel configuration
        fixture: Generated fixture JSON

    Returns:
        DeepDiff object containing differences
    """
    return DeepDiff(
        fixture,
        compiled,
        ignore_order=True,
        verbose_level=2,
    )
