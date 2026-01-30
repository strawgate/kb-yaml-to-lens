"""Tests for YamlPositionResolver."""

import tempfile
from pathlib import Path

import pytest

from dashboard_lint.types import SourcePosition, SourceRange
from dashboard_lint.yaml_position_resolver import MultiFilePositionResolver, YamlPositionResolver


class TestSourcePosition:
    """Tests for SourcePosition dataclass."""

    def test_to_lsp_position(self) -> None:
        """Should convert to LSP-compatible position format."""
        pos = SourcePosition(line=5, character=10)
        lsp_pos = pos.to_lsp_position()

        assert lsp_pos == {'line': 5, 'character': 10}

    def test_zero_indexed(self) -> None:
        """Position should be 0-indexed as per LSP spec."""
        pos = SourcePosition(line=0, character=0)
        assert pos.line == 0
        assert pos.character == 0


class TestSourceRange:
    """Tests for SourceRange dataclass."""

    def test_to_lsp_range(self) -> None:
        """Should convert to LSP-compatible range format."""
        range_ = SourceRange(
            start=SourcePosition(line=5, character=2),
            end=SourcePosition(line=5, character=15),
        )
        lsp_range = range_.to_lsp_range()

        assert lsp_range == {
            'start': {'line': 5, 'character': 2},
            'end': {'line': 5, 'character': 15},
        }

    def test_includes_file_path(self) -> None:
        """Should include file path when set."""
        range_ = SourceRange(
            start=SourcePosition(line=0, character=0),
            end=SourcePosition(line=0, character=5),
            file_path='/path/to/file.yaml',
        )
        assert range_.file_path == '/path/to/file.yaml'


class TestYamlPositionResolver:
    """Tests for YamlPositionResolver."""

    @pytest.fixture
    def sample_yaml(self) -> str:
        """Create sample YAML content for testing."""
        return """name: Test Dashboard
panels:
  - title: Panel 1
    size:
      h: 5
      w: 24
  - title: Panel 2
    size:
      h: 3
      w: 12
filters:
  - field: data_stream.dataset
    equals: test
"""

    @pytest.fixture
    def resolver_from_string(self, sample_yaml: str) -> YamlPositionResolver:
        """Create a resolver from sample YAML string."""
        return YamlPositionResolver.from_string(sample_yaml, '/test/dashboard.yaml')

    def test_from_string(self, sample_yaml: str) -> None:
        """Should create resolver from YAML string."""
        resolver = YamlPositionResolver.from_string(sample_yaml)
        assert resolver is not None
        assert resolver.file_path is None

    def test_from_string_with_path(self, sample_yaml: str) -> None:
        """Should include file path when provided."""
        resolver = YamlPositionResolver.from_string(sample_yaml, '/test/file.yaml')
        assert resolver.file_path == '/test/file.yaml'

    def test_from_file(self, sample_yaml: str) -> None:
        """Should create resolver from YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(sample_yaml)
            f.flush()
            resolver = YamlPositionResolver.from_file(f.name)

        assert resolver is not None
        assert resolver.file_path == f.name

    def test_resolve_root_key(self, resolver_from_string: YamlPositionResolver) -> None:
        """Should resolve position of root-level key."""
        range_ = resolver_from_string.resolve('name')
        assert range_ is not None
        assert range_.start.line == 0
        assert range_.start.character == 0

    def test_resolve_panels_key(self, resolver_from_string: YamlPositionResolver) -> None:
        """Should resolve position of panels key."""
        range_ = resolver_from_string.resolve('panels')
        assert range_ is not None
        assert range_.start.line == 1
        assert range_.start.character == 0

    def test_resolve_panel_index(self, resolver_from_string: YamlPositionResolver) -> None:
        """Should resolve position of indexed panel."""
        range_ = resolver_from_string.resolve('panels[0]')
        assert range_ is not None
        assert range_.start.line == 2  # First panel starts at line 2

        range_second = resolver_from_string.resolve('panels[1]')
        assert range_second is not None
        assert range_second.start.line == 6  # Second panel starts at line 6

    def test_resolve_nested_key(self, resolver_from_string: YamlPositionResolver) -> None:
        """Should resolve position of nested key."""
        range_ = resolver_from_string.resolve('panels[0].size')
        assert range_ is not None
        # Size is nested under first panel

    def test_resolve_invalid_path_returns_none(self, resolver_from_string: YamlPositionResolver) -> None:
        """Should return None for invalid paths."""
        assert resolver_from_string.resolve('nonexistent') is None
        assert resolver_from_string.resolve('panels[999]') is None
        assert resolver_from_string.resolve('panels[0].nonexistent') is None

    def test_resolve_empty_path(self, resolver_from_string: YamlPositionResolver) -> None:
        """Should handle empty path (root document)."""
        range_ = resolver_from_string.resolve('')
        assert range_ is not None
        assert range_.start.line == 0
        assert range_.start.character == 0

    def test_includes_file_path_in_range(self, resolver_from_string: YamlPositionResolver) -> None:
        """Should include file path in resolved range."""
        range_ = resolver_from_string.resolve('name')
        assert range_ is not None
        assert range_.file_path == '/test/dashboard.yaml'

    def test_resolve_filters(self, resolver_from_string: YamlPositionResolver) -> None:
        """Should resolve filters array."""
        range_ = resolver_from_string.resolve('filters')
        assert range_ is not None

        range_item = resolver_from_string.resolve('filters[0]')
        assert range_item is not None


class TestMultiFilePositionResolver:
    """Tests for MultiFilePositionResolver."""

    @pytest.fixture
    def sample_yaml_files(self) -> tuple[Path, Path]:
        """Create two temporary YAML files for testing."""
        with (
            tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f1,
            tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f2,
        ):
            f1.write('name: Dashboard 1\npanels: []\n')
            f2.write('name: Dashboard 2\nfilters: []\n')
            f1.flush()
            f2.flush()
            return Path(f1.name), Path(f2.name)

    def test_caches_resolvers(self, sample_yaml_files: tuple[Path, Path]) -> None:
        """Should cache resolvers for repeated access."""
        path1, _ = sample_yaml_files
        multi_resolver = MultiFilePositionResolver()

        resolver1 = multi_resolver.get_resolver(path1)
        resolver2 = multi_resolver.get_resolver(path1)

        assert resolver1 is resolver2

    def test_different_files_different_resolvers(self, sample_yaml_files: tuple[Path, Path]) -> None:
        """Should create separate resolvers for different files."""
        path1, path2 = sample_yaml_files
        multi_resolver = MultiFilePositionResolver()

        resolver1 = multi_resolver.get_resolver(path1)
        resolver2 = multi_resolver.get_resolver(path2)

        assert resolver1 is not resolver2

    def test_resolve_in_specific_file(self, sample_yaml_files: tuple[Path, Path]) -> None:
        """Should resolve paths in specific files."""
        path1, path2 = sample_yaml_files
        multi_resolver = MultiFilePositionResolver()

        range1 = multi_resolver.resolve(path1, 'panels')
        range2 = multi_resolver.resolve(path2, 'filters')

        assert range1 is not None
        assert range2 is not None
        # Resolve paths to handle symlinks (e.g., /var -> /private/var on macOS)
        assert Path(range1.file_path).resolve() == path1.resolve()
        assert Path(range2.file_path).resolve() == path2.resolve()

    def test_clear_cache(self, sample_yaml_files: tuple[Path, Path]) -> None:
        """Should clear cached resolvers."""
        path1, _ = sample_yaml_files
        multi_resolver = MultiFilePositionResolver()

        resolver1 = multi_resolver.get_resolver(path1)
        multi_resolver.clear_cache()
        resolver2 = multi_resolver.get_resolver(path1)

        assert resolver1 is not resolver2
