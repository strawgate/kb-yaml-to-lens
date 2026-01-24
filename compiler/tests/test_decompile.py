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


class TestMetricDecompilation:
    """Tests for Lens metric decompilation."""

    def test_decompile_count_metric(self) -> None:
        """Test decompiling a count metric."""
        from dashboard_compiler.panels.charts.lens.columns.view import (
            KbnLensFieldMetricColumn,
            KbnLensMetricColumnParams,
        )
        from dashboard_compiler.panels.charts.lens.metrics.config import LensCountAggregatedMetric
        from dashboard_compiler.panels.charts.lens.metrics.decompile import decompile_lens_metric

        column = KbnLensFieldMetricColumn(
            label='Count of records',
            customLabel=None,
            dataType='number',
            operationType='count',
            scale='ratio',
            sourceField='___records___',
            params=KbnLensMetricColumnParams(),
        )
        context = DecompileContext()

        result = decompile_lens_metric(column, 'col1', context=context)

        assert isinstance(result, LensCountAggregatedMetric)
        assert result.aggregation == 'count'
        assert result.field is None
        assert len(context.warnings) == 0

    def test_decompile_sum_metric_with_label(self) -> None:
        """Test decompiling a sum metric with custom label."""
        from dashboard_compiler.panels.charts.lens.columns.view import (
            KbnLensFieldMetricColumn,
            KbnLensMetricColumnParams,
        )
        from dashboard_compiler.panels.charts.lens.metrics.config import LensSumAggregatedMetric
        from dashboard_compiler.panels.charts.lens.metrics.decompile import decompile_lens_metric

        column = KbnLensFieldMetricColumn(
            label='Total Bytes',
            customLabel=True,
            dataType='number',
            operationType='sum',
            scale='ratio',
            sourceField='bytes',
            params=KbnLensMetricColumnParams(),
        )
        context = DecompileContext()

        result = decompile_lens_metric(column, 'col1', context=context)

        assert isinstance(result, LensSumAggregatedMetric)
        assert result.aggregation == 'sum'
        assert result.field == 'bytes'
        assert result.label == 'Total Bytes'
        assert len(context.warnings) == 0

    def test_decompile_formula_metric(self) -> None:
        """Test decompiling a formula metric."""
        from dashboard_compiler.panels.charts.lens.columns.view import (
            KbnLensFormulaColumn,
            KbnLensFormulaColumnParams,
        )
        from dashboard_compiler.panels.charts.lens.metrics.config import LensFormulaMetric
        from dashboard_compiler.panels.charts.lens.metrics.decompile import decompile_lens_metric

        column = KbnLensFormulaColumn(
            label='Error Rate',
            customLabel=True,
            dataType='number',
            operationType='formula',
            isBucketed=False,
            scale='ratio',
            references=[],
            params=KbnLensFormulaColumnParams(
                formula="count(kql='status:error') / count() * 100",
            ),
        )
        context = DecompileContext()

        result = decompile_lens_metric(column, 'col1', context=context)

        assert isinstance(result, LensFormulaMetric)
        assert result.formula == "count(kql='status:error') / count() * 100"
        assert result.label == 'Error Rate'
        assert len(context.warnings) == 0

    def test_decompile_static_value(self) -> None:
        """Test decompiling a static value metric."""
        from dashboard_compiler.panels.charts.lens.columns.view import (
            KbnLensStaticValueColumn,
            KbnLensStaticValueColumnParams,
        )
        from dashboard_compiler.panels.charts.lens.metrics.config import LensStaticValue
        from dashboard_compiler.panels.charts.lens.metrics.decompile import decompile_lens_metric

        column = KbnLensStaticValueColumn(
            label='Maximum',
            customLabel=True,
            dataType='number',
            operationType='static_value',
            scale='ratio',
            params=KbnLensStaticValueColumnParams(value=100),
        )
        context = DecompileContext()

        result = decompile_lens_metric(column, 'col1', context=context)

        assert isinstance(result, LensStaticValue)
        assert result.value == 100
        assert result.label == 'Maximum'
        assert len(context.warnings) == 0


class TestDimensionDecompilation:
    """Tests for Lens dimension decompilation."""

    def test_decompile_date_histogram_dimension(self) -> None:
        """Test decompiling a date histogram dimension."""
        from dashboard_compiler.panels.charts.lens.columns.view import (
            KbnLensDateHistogramDimensionColumn,
            KbnLensDateHistogramDimensionColumnParams,
        )
        from dashboard_compiler.panels.charts.lens.dimensions.config import LensDateHistogramDimension
        from dashboard_compiler.panels.charts.lens.dimensions.decompile import decompile_lens_dimension

        column = KbnLensDateHistogramDimensionColumn(
            label='@timestamp',
            customLabel=None,
            dataType='date',
            operationType='date_histogram',
            scale='interval',
            sourceField='@timestamp',
            params=KbnLensDateHistogramDimensionColumnParams(
                interval='1h',
                includeEmptyRows=True,
                dropPartials=False,
            ),
        )
        context = DecompileContext()

        result = decompile_lens_dimension(column, 'col1', context=context)

        assert isinstance(result, LensDateHistogramDimension)
        assert result.type == 'date_histogram'
        assert result.field == '@timestamp'
        assert result.minimum_interval == '1h'
        assert len(context.warnings) == 0

    def test_decompile_terms_dimension(self) -> None:
        """Test decompiling a terms dimension."""
        from dashboard_compiler.panels.charts.lens.columns.view import (
            KbnLensTermsDimensionColumn,
            KbnLensTermsDimensionColumnParams,
            KbnLensTermsOrderBy,
        )
        from dashboard_compiler.panels.charts.lens.dimensions.config import LensTermsDimension
        from dashboard_compiler.panels.charts.lens.dimensions.decompile import decompile_lens_dimension

        column = KbnLensTermsDimensionColumn(
            label='Top 5 values of service.name',
            customLabel=None,
            dataType='string',
            operationType='terms',
            scale='ordinal',
            sourceField='service.name',
            params=KbnLensTermsDimensionColumnParams(
                size=5,
                orderBy=KbnLensTermsOrderBy(type='column', columnId='metric1'),
                orderDirection='desc',
                otherBucket=True,
                missingBucket=False,
            ),
        )
        context = DecompileContext()

        result = decompile_lens_dimension(column, 'col1', context=context)

        assert isinstance(result, LensTermsDimension)
        assert result.type == 'values'
        assert result.field == 'service.name'
        assert result.size == 5
        assert result.other_bucket is True
        assert result.missing_bucket is False
        assert len(context.warnings) == 0


class TestChartDecompilation:
    """Tests for chart decompilation helpers."""

    def test_get_layer_id_from_layers_array(self) -> None:
        """Test extracting layer ID from layers array."""
        from dashboard_compiler.panels.charts.decompile import get_layer_id

        viz_state = {
            'layers': [{'layerId': 'layer-123'}],
        }

        result = get_layer_id(viz_state)

        assert result == 'layer-123'

    def test_get_layer_id_from_layer_id_field(self) -> None:
        """Test extracting layer ID from layerId field."""
        from dashboard_compiler.panels.charts.decompile import get_layer_id

        viz_state = {
            'layerId': 'layer-456',
        }

        result = get_layer_id(viz_state)

        assert result == 'layer-456'

    def test_get_data_view_from_references(self) -> None:
        """Test extracting data view from references."""
        from dashboard_compiler.panels.charts.decompile import get_data_view_from_references

        references = [
            {'type': 'index-pattern', 'id': 'logs-*', 'name': 'indexpattern-datasource-layer-layer-123'},
        ]

        result = get_data_view_from_references(references, 'layer-123')

        assert result == 'logs-*'
