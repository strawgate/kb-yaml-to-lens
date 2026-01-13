"""Protocol definitions for chart column compilation.

This module defines the ColumnCompiler protocol that abstracts the differences
between Lens and ESQL column compilation, allowing chart compilers to use a
single generic implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class CompileResult[ColumnT, MetricColumnT, DimensionColumnT]:
    """Result of compiling columns for a chart layer.

    This dataclass holds the compiled columns and their accessor IDs,
    abstracting the difference between Lens (dict-based) and ESQL (list-based)
    column storage.

    Attributes:
        columns: The compiled columns in the format appropriate for the compiler type.
        metric_ids: List of metric column IDs in order.
        dimension_ids: List of dimension column IDs in order.
        metrics_by_id: Dictionary mapping metric IDs to compiled metric columns.
        dimensions_by_id: Dictionary mapping dimension IDs to compiled dimension columns.
    """

    columns: ColumnT
    metric_ids: list[str] = field(default_factory=list)
    dimension_ids: list[str] = field(default_factory=list)
    metrics_by_id: dict[str, MetricColumnT] = field(default_factory=dict)
    dimensions_by_id: dict[str, DimensionColumnT] = field(default_factory=dict)


class ColumnCompiler[ColumnT, MetricColumnT, DimensionColumnT, MetricConfigT, DimensionConfigT](ABC):
    """Abstract base class for column compilation.

    This protocol abstracts the differences between Lens and ESQL column
    compilation, allowing chart compilers to use a single generic implementation.

    The key differences abstracted:
    - Lens uses dict[str, KbnLensColumnTypes] for columns
    - ESQL uses list[KbnESQLColumnTypes] for columns
    - Lens dimensions require metric context for ordering
    - ESQL dimensions are pure field references
    """

    @abstractmethod
    def compile_metric(self, metric: MetricConfigT) -> tuple[str, MetricColumnT]:
        """Compile a single metric configuration into a column.

        Args:
            metric: The metric configuration to compile.

        Returns:
            tuple[str, MetricColumnT]: The column ID and compiled column.
        """

    @abstractmethod
    def compile_dimension(
        self, dimension: DimensionConfigT, metrics_by_id: dict[str, MetricColumnT] | None = None
    ) -> tuple[str, DimensionColumnT]:
        """Compile a single dimension configuration into a column.

        Args:
            dimension: The dimension configuration to compile.
            metrics_by_id: Optional mapping of metric IDs to columns for reference.
                          Required for Lens dimensions that need metric context.

        Returns:
            tuple[str, DimensionColumnT]: The column ID and compiled column.
        """

    @abstractmethod
    def build_columns(
        self,
        metrics: list[MetricColumnT],
        metric_ids: list[str],
        dimensions: list[DimensionColumnT],
        dimension_ids: list[str],
    ) -> ColumnT:
        """Build the final column structure from compiled metrics and dimensions.

        Args:
            metrics: List of compiled metric columns.
            metric_ids: List of metric column IDs.
            dimensions: List of compiled dimension columns.
            dimension_ids: List of dimension column IDs.

        Returns:
            ColumnT: The compiled columns in the appropriate format.
        """

    def compile_metrics(self, metrics: list[MetricConfigT]) -> tuple[list[str], list[MetricColumnT], dict[str, MetricColumnT]]:
        """Compile a list of metrics.

        Args:
            metrics: List of metric configurations to compile.

        Returns:
            tuple: (metric_ids, compiled_metrics, metrics_by_id)
        """
        metric_ids: list[str] = []
        compiled_metrics: list[MetricColumnT] = []
        metrics_by_id: dict[str, MetricColumnT] = {}

        for metric in metrics:
            metric_id, compiled = self.compile_metric(metric)
            metric_ids.append(metric_id)
            compiled_metrics.append(compiled)
            metrics_by_id[metric_id] = compiled

        return metric_ids, compiled_metrics, metrics_by_id

    def compile_dimensions(
        self, dimensions: list[DimensionConfigT], metrics_by_id: dict[str, MetricColumnT] | None = None
    ) -> tuple[list[str], list[DimensionColumnT], dict[str, DimensionColumnT]]:
        """Compile a list of dimensions.

        Args:
            dimensions: List of dimension configurations to compile.
            metrics_by_id: Optional mapping of metric IDs to columns for reference.

        Returns:
            tuple: (dimension_ids, compiled_dimensions, dimensions_by_id)
        """
        dimension_ids: list[str] = []
        compiled_dimensions: list[DimensionColumnT] = []
        dimensions_by_id: dict[str, DimensionColumnT] = {}

        for dimension in dimensions:
            dim_id, compiled = self.compile_dimension(dimension, metrics_by_id)
            dimension_ids.append(dim_id)
            compiled_dimensions.append(compiled)
            dimensions_by_id[dim_id] = compiled

        return dimension_ids, compiled_dimensions, dimensions_by_id

    def compile_all(
        self,
        metrics: list[MetricConfigT],
        dimensions: list[DimensionConfigT] | None = None,
    ) -> CompileResult[ColumnT, MetricColumnT, DimensionColumnT]:
        """Compile all metrics and dimensions into a CompileResult.

        Args:
            metrics: List of metric configurations to compile.
            dimensions: Optional list of dimension configurations to compile.

        Returns:
            CompileResult with compiled columns and accessor IDs.
        """
        metric_ids, compiled_metrics, metrics_by_id = self.compile_metrics(metrics)

        dimension_ids: list[str] = []
        compiled_dimensions: list[DimensionColumnT] = []
        dimensions_by_id: dict[str, DimensionColumnT] = {}

        if dimensions is not None:
            dimension_ids, compiled_dimensions, dimensions_by_id = self.compile_dimensions(dimensions, metrics_by_id)

        columns = self.build_columns(compiled_metrics, metric_ids, compiled_dimensions, dimension_ids)

        return CompileResult(
            columns=columns,
            metric_ids=metric_ids,
            dimension_ids=dimension_ids,
            metrics_by_id=metrics_by_id,
            dimensions_by_id=dimensions_by_id,
        )
