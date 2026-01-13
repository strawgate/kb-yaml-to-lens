"""ESQL-specific column compiler implementation.

This module provides the ESQLColumnCompiler class that implements the ColumnCompiler
protocol for ESQL chart column compilation.
"""

from collections.abc import Mapping
from typing import override

from dashboard_compiler.panels.charts.base.protocol import ColumnCompiler
from dashboard_compiler.panels.charts.esql.columns.compile import compile_esql_dimension, compile_esql_metric
from dashboard_compiler.panels.charts.esql.columns.config import ESQLDimensionTypes, ESQLMetricTypes
from dashboard_compiler.panels.charts.esql.columns.view import (
    KbnESQLColumnTypes,
    KbnESQLFieldDimensionColumn,
    KbnESQLMetricColumnTypes,
)


class ESQLColumnCompiler(
    ColumnCompiler[
        list[KbnESQLColumnTypes],
        KbnESQLMetricColumnTypes,
        KbnESQLFieldDimensionColumn,
        ESQLMetricTypes,
        ESQLDimensionTypes,
    ]
):
    """Column compiler for ESQL visualizations.

    Compiles ESQL metric and dimension configurations into Kibana column view models.
    Uses list-based column storage.
    """

    @override
    def compile_metric(self, metric: ESQLMetricTypes) -> tuple[str, KbnESQLMetricColumnTypes]:
        """Compile an ESQL metric configuration into a column.

        Args:
            metric: The ESQL metric configuration to compile.

        Returns:
            tuple[str, KbnESQLMetricColumnTypes]: The column ID and compiled column.
        """
        compiled = compile_esql_metric(metric)
        return compiled.columnId, compiled

    @override
    def compile_dimension(
        self,
        dimension: ESQLDimensionTypes,
        metrics_by_id: Mapping[str, KbnESQLMetricColumnTypes] | None = None,
    ) -> tuple[str, KbnESQLFieldDimensionColumn]:
        """Compile an ESQL dimension configuration into a column.

        Args:
            dimension: The ESQL dimension configuration to compile.
            metrics_by_id: Not used for ESQL dimensions (included for protocol compatibility).

        Returns:
            tuple[str, KbnESQLFieldDimensionColumn]: The column ID and compiled column.
        """
        compiled = compile_esql_dimension(dimension)
        return compiled.columnId, compiled

    @override
    def build_columns(
        self,
        metrics: list[KbnESQLMetricColumnTypes],
        metric_ids: list[str],
        dimensions: list[KbnESQLFieldDimensionColumn],
        dimension_ids: list[str],
    ) -> list[KbnESQLColumnTypes]:
        """Build the final list-based column structure.

        Dimensions are placed before metrics to maintain proper column ordering
        for Kibana datasource state layers.

        Args:
            metrics: List of compiled metric columns.
            metric_ids: List of metric column IDs (not used, included for protocol compatibility).
            dimensions: List of compiled dimension columns.
            dimension_ids: List of dimension column IDs (not used, included for protocol compatibility).

        Returns:
            list[KbnESQLColumnTypes]: List of columns in order.
        """
        # Build list with dimensions first, then metrics, for proper column ordering
        return [*dimensions, *metrics]
