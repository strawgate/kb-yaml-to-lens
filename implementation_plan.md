# Implementation Plan: Lens Visualization Compilation

## Overall Goal

Implement the compilation of Lens visualization configurations (Metric, Pie, etc.) into their corresponding Kibana view models.

## Breakdown

The implementation is broken down into the following parts:

1.  **Metric Visualization Compilation:**
    -   **Input:** `LensMetricChart` or `ESQLMetricsChart` config object, dictionary of compiled columns by ID (`kbn_columns_by_id`).
    -   **Output:** `KbnMetricVisualizationState` view model, layer ID.
    -   **Steps:**
        -   Generate a stable `layerId` (using chart ID or primary metric ID).
        -   Identify `primaryMetricAccessor` (from `chart.primary.id` for Lens, `chart.primary_metric_column` for ESQL).
        -   Identify `secondaryMetricAccessor` (from `chart.secondary.id` for Lens, `chart.secondary_metric_column` for ESQL, if present).
        -   Identify `breakdownByAccessor` (from `chart.breakdown.id` for Lens, `chart.breakdown_by_column` for ESQL, if present).
        -   Determine `maxAccessor` and `showBar` based on the presence of a secondary metric (hardcoded ID '8976bad7-f148-4da1-8352-916f5ae2b730' for now, needs review).
        -   Instantiate `KbnMetricStateVisualizationLayer` with the collected accessors and layer ID.
        -   Instantiate `KbnMetricVisualizationState` with the created layer.
        -   Return the visualization state and layer ID.

2.  **Pie Visualization Compilation:**
    -   **Input:** `LensPieChart` or `ESQLPieChart` config object, dictionary of compiled columns by ID (`kbn_columns_by_id`).
    -   **Output:** `KbnPieVisualizationState` view model, layer ID.
    -   **Steps:**
        -   **TODO: Resolve Syntax Errors in `dashboard_compiler/panels/charts/visualizations/pie/compile.py` first.**
        -   Generate a stable `layerId` (using chart ID, metric ID, and slice-by dimension IDs).
        -   Identify `metric_id` (from `chart.metric.id` for Lens, `chart.metric_column` for ESQL).
        -   Identify `slice_by_ids` (from `chart.slice_by` list for Lens, `chart.slice_by_columns` list for ESQL).
        -   Validate that metric and slice-by dimensions exist in `kbn_columns_by_id`.
        -   Determine `shape` from `chart.appearance.donut` (Lens) or `chart.donut` (ESQL).
        -   Determine `numberDisplay` from `chart.titles_and_text.slice_values` (Lens) or `chart.slice_values` (ESQL).
        -   Determine `categoryDisplay` from `chart.titles_and_text.slice_labels` (Lens) or `chart.slice_labels` (ESQL).
        -   Determine `legendDisplay` from `chart.legend.visible` (Lens) or `chart.legend_visible` (ESQL).
        -   Determine `legendSize` from `chart.legend.width` (Lens) or `chart.legend_width` (ESQL).
        -   Determine `truncateLegend` from `chart.legend.truncate_labels` (Lens) or `chart.truncate_labels` (ESQL).
        -   Instantiate `KbnPieStateVisualizationLayer` with the collected IDs and display options.
        -   Include hardcoded `nestedLegend`, `layerType`, and `colorMapping` based on test data.
        -   Determine `emptySizeRatio` based on `slice_values` being 'integer' (based on test data).
        -   Instantiate `KbnPieVisualizationState` with the determined `shape` and the created layer.
        -   Return the visualization state and layer ID.

3.  **Main Visualization Compilation:**
    -   **Input:** A general visualization config object, dictionary of compiled columns by ID.
    -   **Output:** A tuple containing the visualization state view model (type depends on chart type) and the layer ID.
    -   **Steps:**
        -   Check the `type` field of the input visualization config.
        -   Based on the type, call the appropriate specific compilation function (`compile_lens_metrics_chart`, `compile_lens_pie_chart`, etc.), passing the relevant configuration and compiled columns.
        -   Return the result of the specific compilation function.

## Current Status

-   **Metric Visualization Compilation:**
    -   `dashboard_compiler/panels/charts/visualizations/metric/compile.py`: Created and implemented `compile_lens_metrics_chart` and `compile_esql_lens_metrics_chart` functions based on `test_metric_data.py`. These functions handle primary, secondary, and breakdown columns.
    -   `dashboard_compiler/panels/charts/visualizations/metric/view.py`: Updated `KbnMetricStateVisualizationLayer` to include necessary fields (`maxAccessor`, `showBar`, `secondaryMetricAccessor`, `breakdownByAccessor`).
    -   **Pending:** Review hardcoded `maxAccessor` ID and ensure it's derived correctly if necessary.

-   **Pie Visualization Compilation:**
    -   `dashboard_compiler/panels/charts/visualizations/pie/compile.py`: Attempted to implement `compile_lens_pie_chart` and `compile_esql_pie_chart`. **Currently facing syntax errors in this file that need to be resolved.**
    -   `dashboard_compiler/panels/charts/visualizations/pie/view.py`: Reviewed and seems to align with test data, but may need further refinement once compilation logic is fully implemented.

-   **Main Visualization Compilation:**
    -   `dashboard_compiler/panels/charts/visualizations/compile.py`: File created, but the main compilation logic is not yet implemented.

-   **Dimension Compilation (Related Dependency):**
    -   `dashboard_compiler/panels/charts/dimensions/compile.py`: Implemented compilation logic for date histogram, terms, filters, and intervals dimensions based on `test_lens_dimensions_data.py`. Fixed some linter errors related to attribute access and default values.
    -   `dashboard_compiler/panels/charts/columns/view.py`: Defined Pydantic models for dimension view models.
    -   **Pending:**
        -   Update metric compilation (`compile_lens_metric` in `dashboard_compiler/panels/charts/metrics/compile.py`) to include `columnId` in the returned view model, required for terms dimension `orderBy` logic.
        -   Implement the full logic for `ranges` and `maxBars` in the intervals dimension compilation.
        -   Define more specific Pydantic models for nested parameters in dimension view models (e.g., `orderBy`, `filters`, `ranges`).

## Next Steps

1.  **Resolve Syntax Errors in Pie Compilation:** Fix the syntax errors in `dashboard_compiler/panels/charts/visualizations/pie/compile.py` to enable further implementation and testing. (Highest priority)
2.  **Complete Pie Compilation Logic:** Finish implementing the `compile_lens_pie_chart` and `compile_esql_pie_chart` functions, ensuring all aspects of the pie chart configuration (appearance, titles_and_text, legend) are correctly mapped to the view models based on `test_pie_data.py`. (Depends on Step 1)
3.  **Implement Main Visualization Compilation:** Write the `compile_visualization` function in `dashboard_compiler/panels/charts/visualizations/compile.py` to take a general visualization configuration and call the appropriate specific compilation function (`compile_lens_metrics_chart`, `compile_lens_pie_chart`, etc.) based on the visualization type.
4.  **Address Dimension Compilation TODOs:** Go back to `dashboard_compiler/panels/charts/dimensions/compile.py` and address the pending tasks related to terms and intervals dimensions (`orderBy` `columnId`, `ranges`, `maxBars`). This might require updating the metric compilation as noted.
5.  **Refine View Models:** Continuously review and refine the view models in `dashboard_compiler/panels/charts/columns/view.py` and the `visualizations` subdirectories as the compilation logic is implemented and tested.
6.  **Write/Update Tests:** Ensure comprehensive test coverage for all compilation logic. Update existing tests and add new ones as needed to cover all configuration options and edge cases.
7.  **Integrate with Panel Compilation:** Finally, integrate the visualization compilation into the overall panel compilation process, ensuring that compiled metrics, dimensions, and visualization states are correctly combined. 