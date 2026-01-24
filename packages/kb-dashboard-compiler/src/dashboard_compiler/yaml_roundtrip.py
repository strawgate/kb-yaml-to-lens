"""Round-trip YAML operations that preserve comments and formatting.

This module provides functions for loading and dumping YAML files using ruamel.yaml's
round-trip mode, which preserves comments, indentation, and formatting during edits.
Used specifically for in-place modifications like panel grid updates where preserving
user formatting is critical.
"""

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap


def _create_yaml() -> YAML:
    """Create a configured YAML instance for round-trip operations.

    Returns:
        YAML: A configured ruamel.yaml instance with round-trip mode enabled.
    """
    yaml = YAML(typ='rt')
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    yaml.width = 140
    return yaml


def load_roundtrip(path: str) -> CommentedMap:
    """Load a YAML file preserving comments and formatting.

    Args:
        path: Path to the YAML file to load.

    Returns:
        CommentedMap: The loaded YAML document with all metadata preserved.

    Raises:
        FileNotFoundError: If the file does not exist.
        ruamel.yaml.YAMLError: If the file contains invalid YAML.
        TypeError: If the YAML root is not a mapping.
    """
    yaml = _create_yaml()
    file_path = Path(path)
    with file_path.open(encoding='utf-8') as f:
        document: Any = yaml.load(f)  # pyright: ignore[reportUnknownMemberType, reportAny]
    if not isinstance(document, CommentedMap):
        actual_type = type(document).__name__ if document is not None else 'None'  # pyright: ignore[reportAny]
        msg = f'Expected YAML document root to be a mapping, got {actual_type}'
        raise TypeError(msg)
    return document


def dump_roundtrip(document: CommentedMap, path: str) -> None:
    """Write a YAML document back to file preserving comments and formatting.

    Args:
        document: The YAML document (CommentedMap) to write.
        path: Path where the YAML file will be saved.
    """
    yaml = _create_yaml()
    file_path = Path(path)
    with file_path.open(mode='w', encoding='utf-8') as f:
        yaml.dump(document, f)  # pyright: ignore[reportUnknownMemberType]
