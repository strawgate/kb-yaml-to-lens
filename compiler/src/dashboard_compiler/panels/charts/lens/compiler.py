"""Lens-specific column compiler implementation.

This module provides the LensColumnCompiler class that implements the ColumnCompiler
protocol for Lens chart column compilation.
"""

from collections.abc import Mapping
from typing import override

from dashboard_compiler.panels.charts.base.protocol import ColumnCompiler
from dashboard_compiler.panels.charts.lens.columns.view import (
    KbnLensColumnTypes,
    KbnLensDimensionColumnTypes,
    KbnLensMetricColumnTypes,
)
from dashboard_compiler.panels.charts.lens.dimensions.compile import compile_lens_dimension
from dashboard_compiler.panels.charts.lens.dimensions.config import LensDimensionTypes
from dashboard_compiler.panels.charts.lens.metrics.compile import compile_lens_metric
from dashboard_compiler.panels.charts.lens.metrics.config import LensMetricTypes


class LensColumnCompiler(
    ColumnCompiler[
        dict[str, KbnLensColumnTypes],
        KbnLensMetricColumnTypes,
        KbnLensDimensionColumnTypes,
        LensMetricTypes,
        LensDimensionTypes,
    ]
):
    """Column compiler for Lens visualizations.

    Compiles Lens metric and dimension configurations into Kibana column view models.
    Uses dict-based column storage where column IDs are keys.
    """

    @override
    def compile_metric(self, metric: LensMetricTypes) -> tuple[str, KbnLensMetricColumnTypes]:
        """Compile a Lens metric configuration into a column.

        Args:
            metric: The Lens metric configuration to compile.

        Returns:
            tuple[str, KbnLensMetricColumnTypes]: The column ID and compiled column.
        """
        return compile_lens_metric(metric)

    @override
    def compile_dimension(
        self,
        dimension: LensDimensionTypes,
        metrics_by_id: Mapping[str, KbnLensMetricColumnTypes] | None = None,
    ) -> tuple[str, KbnLensDimensionColumnTypes]:
        """Compile a Lens dimension configuration into a column.

        Args:
            dimension: The Lens dimension configuration to compile.
            metrics_by_id: Mapping of metric IDs to columns for reference.
                          Required for proper ordering of terms dimensions.

        Returns:
            tuple[str, KbnLensDimensionColumnTypes]: The column ID and compiled column.
        """
        if metrics_by_id is None:
            metrics_by_id = {}
        return compile_lens_dimension(dimension, kbn_metric_column_by_id=metrics_by_id)

    @override
    def build_columns(
        self,
        metrics: list[KbnLensMetricColumnTypes],
        metric_ids: list[str],
        dimensions: list[KbnLensDimensionColumnTypes],
        dimension_ids: list[str],
    ) -> dict[str, KbnLensColumnTypes]:
        """Build the final dict-based column structure.

        Dimensions are placed before metrics to maintain proper column ordering
        for Kibana datasource state layers.

        Args:
            metrics: List of compiled metric columns.
            metric_ids: List of metric column IDs.
            dimensions: List of compiled dimension columns.
            dimension_ids: List of dimension column IDs.

        Returns:
            dict[str, KbnLensColumnTypes]: Dictionary mapping column IDs to columns.
        """
        # Build dict with dimensions first, then metrics, for proper column ordering
        dimension_columns = dict(zip(dimension_ids, dimensions, strict=True))
        metric_columns = dict(zip(metric_ids, metrics, strict=True))
        return {**dimension_columns, **metric_columns}
