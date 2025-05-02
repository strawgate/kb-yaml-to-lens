"""Compile Lens metrics into their Kibana view models."""
from dashboard_compiler.panels.lens.metrics.config import LensAggregatedMetricTypes, LensFormulaMetric, LensMetricTypes
from dashboard_compiler.panels.lens.view import KbnLensColumnTypes, KbnLensFieldSourcedColunn, KbnLensFormulaSourcedColumn
from dashboard_compiler.shared.config import stable_id_generator


def compile_lens_formula_metric(
    metric_id: str, metric: LensFormulaMetric,
) -> tuple[str, KbnLensFormulaSourcedColumn]:
    """Compile a LensFormulaMetric object into its Kibana view model.

    Args:
        metric_id (str): The ID of the metric.
        metric (LensFormulaMetric): The LensFormulaMetric object to compile.

    Returns:
        tuple[str, KbnLensFormulaSourcedColumn]: A tuple containing the metric ID and its compiled KbnLensFormulaSourcedColumn.

    """
    return metric_id, KbnLensFormulaSourcedColumn(
        label=metric.label,
        customLabel=metric.label is not None or None,
        dataType='number',
        operationType=metric.type,
        scale='ratio',
        formula=metric.formula,
        isBucketed=False,
        params={
            'emptyAsNull': True,
        },
    )


def compile_lens_field_sourced_metric(
    metric_id: str, metric: LensAggregatedMetricTypes,
) -> tuple[str, KbnLensFieldSourcedColunn]:
    """Compile a LensMetricTypes object into its Kibana view model.

    Args:
        metric_id (str): The ID of the metric.
        metric (LensMetricTypes): The LensMetricTypes object to compile.

    Returns:
        tuple[str, KbnColumn]: A tuple containing the metric ID and its compiled KbnColumn.

    """
    return metric_id, KbnLensFieldSourcedColunn(
        label=metric.label,
        customLabel=metric.label is not None or None,
        dataType='number',
        operationType=metric.type,
        scale='ratio',
        sourceField=metric.field,
        isBucketed=False,
        params={
            'emptyAsNull': True,
        },
    )


def compile_lens_metric(metric_id: str, metric: LensMetricTypes) -> tuple[str, KbnLensColumnTypes]:
    """Compile a single LensMetricTypes object into its Kibana view model.

    Args:
        metric_id (str): The ID of the metric.
        metric (LensMetricTypes): The LensMetricTypes object to compile.

    Returns:
        tuple[str, KbnColumn]: A tuple containing the metric ID and its compiled KbnColumn.

    """
    if isinstance(metric, LensFormulaMetric):
        return compile_lens_formula_metric(metric_id, metric)

    return compile_lens_field_sourced_metric(metric_id, metric)


def compile_lens_metrics(metrics: list[LensMetricTypes]) -> dict[str, KbnLensColumnTypes]:
    """Compile a list of LensMetricTypes into their Kibana view model representation.

    Args:
        metrics (list[LensMetricTypes]): The list of LensMetricTypes objects to compile.

    Returns:
        tuple[dict[str, KbnLensColumnTypes], dict[str, str]]: A tuple containing two dictionaries:
            - metrics_by_id: A dictionary mapping metric IDs to their compiled KbnLensColumnTypes.

    """
    metrics_by_id = {}

    for i, metric in enumerate(metrics):
        metric_id = metric.id or stable_id_generator([str(i), metric.type, metric.label, getattr(metric, 'field', '')])

        compiled_metric = compile_lens_metric(metric_id, metric)

        metrics_by_id[compiled_metric[0]] = compiled_metric[1]

    return metrics_by_id
