"""Tests for CLI docs commands."""

import sys
from unittest.mock import MagicMock

from click.testing import CliRunner

from dashboard_compiler.cli import cli
from dashboard_compiler.cli_docs import docs


class TestDocsCommandRegistration:
    """Tests for docs command registration."""

    def test_docs_command_is_registered(self) -> None:
        """Test that docs command is registered with the main CLI."""
        command_names = list(cli.commands)
        assert 'docs' in command_names

    def test_docs_command_has_subcommands(self) -> None:
        """Test that docs command has the expected subcommands."""
        assert hasattr(docs, 'commands')
        subcommand_names = list(docs.commands.keys())
        assert 'llms-full' in subcommand_names
        assert 'list-guides' in subcommand_names
        assert 'guide' in subcommand_names


class TestDocsCommand:
    """Tests for docs command behavior and llms-full subcommand."""

    def test_docs_without_subcommand_shows_help(self) -> None:
        """Test that docs command without subcommand displays help."""
        runner = CliRunner()
        result = runner.invoke(docs, [])
        assert result.exit_code == 0
        assert 'Usage:' in result.output
        assert 'llms-full' in result.output

    def test_llms_full_outputs_full_content(self) -> None:
        """Test that llms-full outputs full documentation content."""
        runner = CliRunner()
        mock_content = 'Full documentation content here'

        # Create a mock module
        mock_module = MagicMock()
        mock_module.get_full_docs = MagicMock(return_value=mock_content)

        # Temporarily replace the module in sys.modules
        original = sys.modules.get('kb_dashboard_docs')
        sys.modules['kb_dashboard_docs'] = mock_module
        try:
            result = runner.invoke(docs, ['llms-full'])
        finally:
            if original is not None:
                sys.modules['kb_dashboard_docs'] = original
            else:
                sys.modules.pop('kb_dashboard_docs', None)

        assert result.exit_code == 0
        assert mock_content in result.output

    def test_llms_full_handles_file_not_found(self) -> None:
        """Test that llms-full handles missing documentation file."""
        runner = CliRunner()

        def raise_file_not_found() -> str:
            msg = 'llms-full.txt not found'
            raise FileNotFoundError(msg)

        mock_module = MagicMock()
        mock_module.get_full_docs = raise_file_not_found

        original = sys.modules.get('kb_dashboard_docs')
        sys.modules['kb_dashboard_docs'] = mock_module
        try:
            result = runner.invoke(docs, ['llms-full'])
        finally:
            if original is not None:
                sys.modules['kb_dashboard_docs'] = original
            else:
                sys.modules.pop('kb_dashboard_docs', None)

        assert result.exit_code == 1
        assert 'not bundled' in result.output.lower() or 'installation issue' in result.output.lower()

    def test_llms_full_handles_import_error(self) -> None:
        """Test that llms-full handles missing package."""
        runner = CliRunner()

        # Create a mock that raises ImportError when accessed
        class MockModule:
            def __getattr__(self, name: str) -> None:
                msg = 'No module named kb_dashboard_docs'
                raise ImportError(msg)

        original = sys.modules.get('kb_dashboard_docs')
        sys.modules['kb_dashboard_docs'] = MockModule()
        try:
            result = runner.invoke(docs, ['llms-full'])
        finally:
            if original is not None:
                sys.modules['kb_dashboard_docs'] = original
            else:
                sys.modules.pop('kb_dashboard_docs', None)

        assert result.exit_code == 1
        # The error message should mention installation issue or not installed
        assert 'not installed' in result.output.lower() or 'installation' in result.output.lower()


class TestListGuidesCommand:
    """Tests for the list-guides command."""

    def test_list_guides_outputs_available_guides(self) -> None:
        """Test that list-guides outputs available guide names."""
        runner = CliRunner()
        mock_guides = ['esql-language-reference', 'otel-dashboard-guide']

        mock_module = MagicMock()
        mock_module.list_guides = MagicMock(return_value=mock_guides)

        original = sys.modules.get('kb_dashboard_docs')
        sys.modules['kb_dashboard_docs'] = mock_module
        try:
            result = runner.invoke(docs, ['list-guides'])
        finally:
            if original is not None:
                sys.modules['kb_dashboard_docs'] = original
            else:
                sys.modules.pop('kb_dashboard_docs', None)

        assert result.exit_code == 0
        assert 'esql-language-reference' in result.output
        assert 'otel-dashboard-guide' in result.output

    def test_list_guides_handles_empty_list(self) -> None:
        """Test that list-guides handles no guides available."""
        runner = CliRunner()

        mock_module = MagicMock()
        mock_module.list_guides = MagicMock(return_value=[])

        original = sys.modules.get('kb_dashboard_docs')
        sys.modules['kb_dashboard_docs'] = mock_module
        try:
            result = runner.invoke(docs, ['list-guides'])
        finally:
            if original is not None:
                sys.modules['kb_dashboard_docs'] = original
            else:
                sys.modules.pop('kb_dashboard_docs', None)

        assert result.exit_code == 0
        assert 'no guides' in result.output.lower()

    def test_list_guides_handles_import_error(self) -> None:
        """Test that list-guides handles missing package."""
        runner = CliRunner()

        # Create a mock that raises ImportError when list_guides is accessed
        class MockModule:
            def __getattr__(self, name: str) -> None:
                msg = 'No module named kb_dashboard_docs'
                raise ImportError(msg)

        original = sys.modules.get('kb_dashboard_docs')
        sys.modules['kb_dashboard_docs'] = MockModule()
        try:
            result = runner.invoke(docs, ['list-guides'])
        finally:
            if original is not None:
                sys.modules['kb_dashboard_docs'] = original
            else:
                sys.modules.pop('kb_dashboard_docs', None)

        assert result.exit_code == 1
        assert 'not installed' in result.output.lower()


class TestGetGuideCommand:
    """Tests for the guide command."""

    def test_guide_outputs_content(self) -> None:
        """Test that guide command outputs guide content."""
        runner = CliRunner()
        mock_content = '# OTel Dashboard Guide\n\nContent here...'

        mock_module = MagicMock()
        mock_module.get_guide = MagicMock(return_value=mock_content)

        original = sys.modules.get('kb_dashboard_docs')
        sys.modules['kb_dashboard_docs'] = mock_module
        try:
            result = runner.invoke(docs, ['guide', 'otel-dashboard-guide'])
        finally:
            if original is not None:
                sys.modules['kb_dashboard_docs'] = original
            else:
                sys.modules.pop('kb_dashboard_docs', None)

        assert result.exit_code == 0
        assert mock_content in result.output

    def test_guide_handles_not_found(self) -> None:
        """Test that guide command handles missing guide."""
        runner = CliRunner()

        def raise_not_found(name: str) -> str:
            msg = f"Guide '{name}' not found. Available guides: guide1, guide2"
            raise FileNotFoundError(msg)

        mock_module = MagicMock()
        mock_module.get_guide = raise_not_found

        original = sys.modules.get('kb_dashboard_docs')
        sys.modules['kb_dashboard_docs'] = mock_module
        try:
            result = runner.invoke(docs, ['guide', 'nonexistent'])
        finally:
            if original is not None:
                sys.modules['kb_dashboard_docs'] = original
            else:
                sys.modules.pop('kb_dashboard_docs', None)

        assert result.exit_code == 1
        assert 'not found' in result.output.lower()

    def test_guide_handles_import_error(self) -> None:
        """Test that guide command handles missing package."""
        runner = CliRunner()

        # Create a mock that raises ImportError when get_guide is accessed
        class MockModule:
            def __getattr__(self, name: str) -> None:
                msg = 'No module named kb_dashboard_docs'
                raise ImportError(msg)

        original = sys.modules.get('kb_dashboard_docs')
        sys.modules['kb_dashboard_docs'] = MockModule()
        try:
            result = runner.invoke(docs, ['guide', 'any-guide'])
        finally:
            if original is not None:
                sys.modules['kb_dashboard_docs'] = original
            else:
                sys.modules.pop('kb_dashboard_docs', None)

        assert result.exit_code == 1
        assert 'not installed' in result.output.lower()
