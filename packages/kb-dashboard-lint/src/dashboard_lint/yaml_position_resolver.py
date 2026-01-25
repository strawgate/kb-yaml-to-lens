"""YAML position resolver for mapping violation paths to source locations.

This module provides utilities for resolving Dashboard object paths (like
'panels[2].lens.metrics[0]') back to line/column positions in the original
YAML source file. This enables IDE-style diagnostics with precise highlighting.

ruamel.yaml lacks type stubs and returns dynamic types from load operations.
The `lc` (line/column) attribute on CommentedMap/CommentedSeq is also dynamic.
"""

# pyright: reportAny=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false

import io
import re
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from dashboard_lint.types import SourcePosition, SourceRange

# Pattern to parse path segments like "panels[2]" or "metrics[0]" or "lens"
PATH_SEGMENT_PATTERN = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)(?:\[(\d+)\])?$')

# Default character span for end position estimation when no better info available
_DEFAULT_HIGHLIGHT_WIDTH = 40


class YamlPositionResolver:
    """Resolves Dashboard object paths to YAML source positions.

    This class parses YAML files using ruamel.yaml's round-trip mode which
    preserves line and column information for all nodes. It then provides
    methods to look up positions for paths like 'panels[2].lens.metrics[0]'.

    Usage:
        resolver = YamlPositionResolver.from_file('/path/to/dashboard.yaml')
        position = resolver.resolve('panels[2]')
        if position is not None:
            print(f"Line {position.start.line}, Column {position.start.character}")

    """

    def __init__(self, document: CommentedMap, file_path: str | None = None) -> None:
        """Initialize the resolver with a parsed YAML document.

        Args:
            document: A ruamel.yaml CommentedMap with position information.
            file_path: Optional path to the source file for context.

        """
        self._document: CommentedMap = document
        self._file_path: str | None = file_path

    @classmethod
    def from_file(cls, file_path: str | Path) -> 'YamlPositionResolver':
        """Create a resolver from a YAML file.

        Args:
            file_path: Path to the YAML file to parse.

        Returns:
            A YamlPositionResolver instance.

        Raises:
            FileNotFoundError: If the file does not exist.
            ruamel.yaml.YAMLError: If the file contains invalid YAML.

        """
        path = Path(file_path)
        yaml = YAML(typ='rt')
        yaml.preserve_quotes = True

        with path.open(encoding='utf-8') as f:
            document: Any = yaml.load(f)

        if not isinstance(document, CommentedMap):
            actual_type = type(document).__name__ if document is not None else 'None'
            msg = f'Expected YAML document root to be a mapping, got {actual_type}'
            raise TypeError(msg)

        return cls(document, str(path))

    @classmethod
    def from_string(cls, yaml_content: str, file_path: str | None = None) -> 'YamlPositionResolver':
        """Create a resolver from a YAML string.

        Args:
            yaml_content: YAML content as a string.
            file_path: Optional file path for context in error messages.

        Returns:
            A YamlPositionResolver instance.

        Raises:
            ruamel.yaml.YAMLError: If the content is invalid YAML.

        """
        yaml = YAML(typ='rt')
        yaml.preserve_quotes = True

        document: Any = yaml.load(io.StringIO(yaml_content))

        if not isinstance(document, CommentedMap):
            actual_type = type(document).__name__ if document is not None else 'None'
            msg = f'Expected YAML document root to be a mapping, got {actual_type}'
            raise TypeError(msg)

        return cls(document, file_path)

    def _parse_path(self, path: str) -> list[tuple[str, int | None]]:
        """Parse a path string into segments.

        Args:
            path: A path like 'panels[2].lens.metrics[0]'.

        Returns:
            List of (key_name, optional_index) tuples.

        Raises:
            ValueError: If the path format is invalid.

        """
        segments: list[tuple[str, int | None]] = []

        for part in path.split('.'):
            if len(part) == 0:
                continue

            match = PATH_SEGMENT_PATTERN.match(part)
            if match is None:
                msg = f"Invalid path segment: '{part}'"
                raise ValueError(msg)

            key = match.group(1)
            index_str = match.group(2)
            index = int(index_str) if index_str is not None else None
            segments.append((key, index))

        return segments

    def _navigate_to_node(
        self,
        segments: list[tuple[str, int | None]],
    ) -> tuple[CommentedMap | CommentedSeq | None, str | int | None]:
        """Navigate through the document to find a node.

        Args:
            segments: Parsed path segments.

        Returns:
            Tuple of (parent_node, key_or_index) where the target can be found,
            or (None, None) if the path doesn't exist.

        """
        not_found: tuple[None, None] = (None, None)

        if len(segments) == 0:
            return self._document, None

        current: CommentedMap | CommentedSeq = self._document

        # Navigate through all but the last segment
        for key, index in segments[:-1]:
            if not isinstance(current, CommentedMap) or key not in current:
                return not_found

            node = current[key]

            if index is not None:
                if not isinstance(node, CommentedSeq) or index >= len(node):
                    return not_found
                current = node[index]
            else:
                current = node

        # Handle the last segment
        last_key, last_index = segments[-1]

        if not isinstance(current, CommentedMap) or last_key not in current:
            return not_found

        if last_index is not None:
            node = current[last_key]
            if not isinstance(node, CommentedSeq) or last_index >= len(node):
                return not_found
            return node, last_index

        return current, last_key

    def _get_key_position(self, parent: CommentedMap, key: str) -> SourcePosition | None:
        """Get the line/column position of a key in a mapping, or None if unavailable."""
        if not hasattr(parent, 'lc') or parent.lc is None:
            return None

        try:
            line, col = parent.lc.key(key)
            return SourcePosition(line=line, character=col)
        except (KeyError, AttributeError):
            return None

    def _get_item_position(self, parent: CommentedSeq, index: int) -> SourcePosition | None:
        """Get the line/column position of an item in a sequence, or None if unavailable."""
        if not hasattr(parent, 'lc') or parent.lc is None:
            return None

        try:
            line, col = parent.lc.item(index)
            return SourcePosition(line=line, character=col)
        except (IndexError, KeyError, AttributeError):
            return None

    def _estimate_end_position(
        self,
        start: SourcePosition,
        parent: CommentedMap | CommentedSeq,
        key_or_index: str | int | None,
    ) -> SourcePosition:
        """Estimate the end position for a node.

        For simple values, we use the end of the line.
        For complex values (mappings/sequences), we try to find the next sibling.

        Args:
            start: The start position.
            parent: The parent node.
            key_or_index: The key or index of the target node.

        Returns:
            An estimated end position.

        """
        if isinstance(parent, CommentedMap) and isinstance(key_or_index, str):
            keys = list(parent.keys())
            try:
                key_idx = keys.index(key_or_index)
                if key_idx + 1 < len(keys):
                    next_key = keys[key_idx + 1]
                    next_pos = self._get_key_position(parent, next_key)
                    if next_pos is not None and next_pos.line > start.line:
                        return SourcePosition(line=next_pos.line - 1, character=0)
            except (ValueError, KeyError):
                pass

            # Default: highlight the key name
            return SourcePosition(line=start.line, character=start.character + len(key_or_index))

        if isinstance(parent, CommentedSeq) and isinstance(key_or_index, int):
            if key_or_index + 1 < len(parent):
                next_pos = self._get_item_position(parent, key_or_index + 1)
                if next_pos is not None and next_pos.line > start.line:
                    return SourcePosition(line=next_pos.line - 1, character=0)

            # Default: end of line
            return SourcePosition(line=start.line, character=start.character + _DEFAULT_HIGHLIGHT_WIDTH)

        # Fallback: end of line
        return SourcePosition(line=start.line, character=start.character + _DEFAULT_HIGHLIGHT_WIDTH)

    def resolve(self, path: str) -> SourceRange | None:
        """Resolve a path to its source range in the YAML file.

        Args:
            path: A path like 'panels[2]' or 'panels[2].lens.metrics[0]'.

        Returns:
            SourceRange if the path can be resolved, None otherwise.

        """
        try:
            segments = self._parse_path(path)
        except ValueError:
            return None

        if len(segments) == 0:
            # Root document
            return SourceRange(
                start=SourcePosition(line=0, character=0),
                end=SourcePosition(line=0, character=0),
                file_path=self._file_path,
            )

        parent, key_or_index = self._navigate_to_node(segments)

        if parent is None:
            return None

        # Get start position
        start: SourcePosition | None = None

        if isinstance(parent, CommentedMap) and isinstance(key_or_index, str):
            start = self._get_key_position(parent, key_or_index)
        elif isinstance(parent, CommentedSeq) and isinstance(key_or_index, int):
            start = self._get_item_position(parent, key_or_index)

        if start is None:
            return None

        # Estimate end position
        end = self._estimate_end_position(start, parent, key_or_index)

        return SourceRange(start=start, end=end, file_path=self._file_path)

    def resolve_dashboard(self, dashboard_index: int = 0) -> SourceRange | None:
        """Resolve the position of a dashboard in a multi-dashboard file.

        For files with a 'dashboards' key, resolves dashboards[index].
        For single dashboard files, resolves the root.

        Args:
            dashboard_index: Index of the dashboard in the dashboards array.

        Returns:
            SourceRange if found, None otherwise.

        """
        if 'dashboards' in self._document:
            return self.resolve(f'dashboards[{dashboard_index}]')

        # Single dashboard file - return root position
        return SourceRange(
            start=SourcePosition(line=0, character=0),
            end=SourcePosition(line=0, character=0),
            file_path=self._file_path,
        )

    @property
    def file_path(self) -> str | None:
        """Get the file path associated with this resolver."""
        return self._file_path


class MultiFilePositionResolver:
    """Manages position resolvers for multiple YAML files.

    This class caches resolvers for each file to avoid reparsing.
    """

    def __init__(self) -> None:
        """Initialize the multi-file resolver."""
        self._resolvers: dict[str, YamlPositionResolver] = {}

    def get_resolver(self, file_path: str | Path) -> YamlPositionResolver:
        """Get or create a resolver for a file.

        Args:
            file_path: Path to the YAML file.

        Returns:
            A YamlPositionResolver for the file.

        """
        # Normalize path to ensure consistent cache keys for the same file
        canonical_path = str(Path(file_path).resolve())
        if canonical_path not in self._resolvers:
            self._resolvers[canonical_path] = YamlPositionResolver.from_file(canonical_path)
        return self._resolvers[canonical_path]

    def resolve(self, file_path: str | Path, path: str) -> SourceRange | None:
        """Resolve a path in a specific file.

        Args:
            file_path: Path to the YAML file.
            path: The path to resolve within the file.

        Returns:
            SourceRange if found, None otherwise.

        """
        resolver = self.get_resolver(file_path)
        return resolver.resolve(path)

    def clear_cache(self) -> None:
        """Clear all cached resolvers."""
        self._resolvers.clear()
