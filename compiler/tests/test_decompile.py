"""Unit tests for the decompiler."""

import pytest

from dashboard_compiler.filters.config import ExistsFilter, PhraseFilter
from dashboard_compiler.filters.decompile import decompile_filter, decompile_filters
from dashboard_compiler.filters.view import KbnFilter, KbnFilterMeta
from dashboard_compiler.queries.config import KqlQuery, LuceneQuery
from dashboard_compiler.queries.decompile import decompile_query
from dashboard_compiler.queries.view import KbnQuery
from dashboard_compiler.shared.decompile_context import DecompileContext


class TestQueryDecompilation:
    """Tests for query decompilation."""

    def test_decompile_kql_query(self) -> None:
        """Test decompiling a KQL query."""
        kbn_query = KbnQuery(query='host.name: "test"', language='kuery')
        context = DecompileContext()

        result = decompile_query(kbn_query, context=context)

        assert isinstance(result, KqlQuery)
        assert result.kql == 'host.name: "test"'
        assert len(context.warnings) == 0

    def test_decompile_lucene_query(self) -> None:
        """Test decompiling a Lucene query."""
        kbn_query = KbnQuery(query='status:200', language='lucene')
        context = DecompileContext()

        result = decompile_query(kbn_query, context=context)

        assert isinstance(result, LuceneQuery)
        assert result.lucene == 'status:200'
        assert len(context.warnings) == 0

    def test_decompile_empty_query(self) -> None:
        """Test decompiling an empty query returns None."""
        kbn_query = KbnQuery(query='', language='kuery')
        context = DecompileContext()

        result = decompile_query(kbn_query, context=context)

        assert result is None
        assert len(context.warnings) == 0


class TestFilterDecompilation:
    """Tests for filter decompilation."""

    def test_decompile_exists_filter(self) -> None:
        """Test decompiling an exists filter."""
        kbn_filter = KbnFilter(
            meta=KbnFilterMeta(
                type='exists',
                key='host.name',
                field='host.name',
                disabled=False,
                negate=False,
            ),
            state=None,
            query={'exists': {'field': 'host.name'}},
        )
        context = DecompileContext()

        result = decompile_filter(kbn_filter, context=context)

        assert isinstance(result, ExistsFilter)
        assert result.exists == 'host.name'
        assert len(context.warnings) == 0

    def test_decompile_phrase_filter(self) -> None:
        """Test decompiling a phrase filter."""
        kbn_filter = KbnFilter(
            meta=KbnFilterMeta(
                type='phrase',
                key='status',
                field='status',
                params={'query': 'active'},
                disabled=False,
                negate=False,
            ),
            state=None,
            query={'match_phrase': {'status': 'active'}},
        )
        context = DecompileContext()

        result = decompile_filter(kbn_filter, context=context)

        assert isinstance(result, PhraseFilter)
        assert result.field == 'status'
        assert result.equals == 'active'
        assert len(context.warnings) == 0

    def test_decompile_filters_list(self) -> None:
        """Test decompiling a list of filters."""
        kbn_filters = [
            KbnFilter(
                meta=KbnFilterMeta(
                    type='exists',
                    key='field1',
                    field='field1',
                    disabled=False,
                    negate=False,
                ),
                state=None,
                query={'exists': {'field': 'field1'}},
            ),
            KbnFilter(
                meta=KbnFilterMeta(
                    type='exists',
                    key='field2',
                    field='field2',
                    disabled=False,
                    negate=False,
                ),
                state=None,
                query={'exists': {'field': 'field2'}},
            ),
        ]
        context = DecompileContext()

        results = decompile_filters(kbn_filters, context=context)

        assert len(results) == 2
        assert all(isinstance(f, ExistsFilter) for f in results)


class TestDecompileContext:
    """Tests for DecompileContext."""

    def test_context_collects_warnings(self) -> None:
        """Test that context collects warnings."""
        context = DecompileContext()

        context.warn('Test warning 1')
        context.warn('Test warning 2', panel_title='Test Panel')

        assert len(context.warnings) == 2
        assert context.warnings[0].message == 'Test warning 1'
        assert context.warnings[1].panel_title == 'Test Panel'

    def test_strict_mode_raises_on_warning(self) -> None:
        """Test that strict mode raises DecompileError on warning."""
        from dashboard_compiler.shared.decompile_context import DecompileError

        context = DecompileContext(strict=True)

        with pytest.raises(DecompileError):
            context.warn('This should raise')
