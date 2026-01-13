"""Factory functions for Lens form-based datasource layer construction."""

from dashboard_compiler.panels.charts.lens.columns.view import KbnLensColumnTypes
from dashboard_compiler.panels.charts.view import KbnFormBasedDataSourceStateLayer


def compile_form_based_layer(
    columns: dict[str, KbnLensColumnTypes],
    sampling: int = 1,
) -> KbnFormBasedDataSourceStateLayer:
    """Construct a KbnFormBasedDataSourceStateLayer from compiled columns.

    This factory function centralizes layer construction for all Lens-based chart types,
    ensuring consistent column ordering and default values.

    Args:
        columns: Dictionary mapping column IDs to their compiled column definitions.
        sampling: Sampling rate for the layer. Defaults to 1 (no sampling).

    Returns:
        KbnFormBasedDataSourceStateLayer with columns ordered by their dictionary keys.
    """
    return KbnFormBasedDataSourceStateLayer(
        columns=columns,
        columnOrder=list(columns.keys()),
        sampling=sampling,
    )
