# Documentation Correction Plan

This plan outlines the necessary corrections to the markdown documentation based on the current state of the configuration language defined in the `config.py` files.

## Discrepancies and Required Corrections

Based on the review of `config.py` and `.md` files, the following discrepancies and required corrections have been identified:

### dashboard_compiler/filters/config.md

*   **Update Filter Types:** The `config.py` defines `CustomFilter`, `NegateFilter`, `AndFilter`, and `OrFilter` which are not fully or accurately reflected in the `filters/config.md`. The markdown needs to be updated to include detailed descriptions and examples for these filter types, especially the junction (`AndFilter`, `OrFilter`) and modifier (`NegateFilter`) types, and the `CustomFilter` with its `dsl` field.
*   **Panel Filters Section:** The "Panel Filters" section in `filters/config.md` describes a different structure (`type`, `value`, `operator`, `negate`) than what is implied by the `FilterTypes` used in `dashboard/config.py` for the `filters` field within the `Dashboard` model. It seems panel filters should use the same filter types as dashboard filters. This section needs to be corrected or removed if panel-specific filter types are no longer supported or defined differently.

### dashboard_compiler/panels/base.md

*   **Add `hide_title` field:** The `BasePanel` in `panels/config.py` includes a `hide_title` field which is not documented in `panels/base.md`. This field and its description should be added.
*   **Update Panel Types List:** The list of Panel Types should be reviewed and updated to match the `PanelTypes` defined in `panels/config.py`. Specifically, `Map Panel` is listed in the markdown but not in the `PanelTypes` union in `panels/config.py`. `LensPanel` and `ESQLPanel` are defined in `panels/charts/config.py` and should be added to the list of panel types in `panels/base.md`.

### dashboard_compiler/panels/images/image.md

*   **Incorrect Content Field:** The markdown incorrectly lists a `content` field. The `ImagePanel` in `panels/images/config.py` defines `from_url`, `fit`, `description`, and `background_color`. The markdown needs to be completely rewritten to reflect the actual fields of the `ImagePanel`.
*   **Update Example:** The example in the markdown is for a markdown panel, not an image panel. A correct example for an image panel using the actual fields is needed.

### dashboard_compiler/panels/markdown/markdown.md

*   **Add `font_size` and `links_in_new_tab` fields:** The `MarkdownPanel` in `panels/markdown/config.py` includes `font_size` and `links_in_new_tab` fields which are not documented in `markdown.md`. These fields and their descriptions should be added.

### dashboard_compiler/panels/charts/metrics/metric.md

*   **Update Metric Types:** The `config.py` defines `ESQLMetricTypes` and `LensMetricTypes` with various specific metric types (`LensFormulaMetric`, `LensAggregatedMetricTypes` including `LensOtherAggregatedMetric`, `LensLastValueAggregatedMetric`, `LensCountAggregatedMetric`, `LensSumAggregatedMetric`, `LensPercentileRankAggregatedMetric`, `LensPercentileAggregatedMetric`, and `ESQLMetric`). The markdown needs to be updated to accurately reflect these distinct types and their specific fields and descriptions. The current markdown is a simplified representation.
*   **Add Metric Format Documentation:** The `LensMetricFormatTypes` including `LensMetricFormat` and `LensCustomMetricFormat` are defined in `config.py` but not documented in `metric.md`. Documentation for how to specify metric formatting should be added.
*   **Review and Update Examples:** The examples should be reviewed and updated to align with the specific metric types defined in `config.py`.

### dashboard_compiler/panels/charts/dimensions/dimension.md

*   **Update Dimension Types:** The `config.py` defines `LensDimensionTypes` with `LensTopValuesDimension`, `LensDateHistogramDimension`, `LensFiltersDimension`, and `LensIntervalsDimension`, as well as `ESQLDimensionTypes` with `ESQLDimension`. The markdown needs to be updated to accurately reflect these distinct types and their specific fields and descriptions. The current markdown is a simplified representation.
*   **Add `CollapseAggregationEnum` Documentation:** The `CollapseAggregationEnum` is defined in `config.py` and used in `LensIntervalsDimension` and `LensDateHistogramDimension` but not documented. This enum and its usage should be documented.
*   **Review and Update Examples:** The examples should be reviewed and updated to align with the specific dimension types defined in `config.py`.

### dashboard_compiler/panels/links/links.md

*   **Update Link Types:** The `config.py` defines `LinkTypes` as `DashboardLink | UrlLink` with specific fields for each (`dashboard`, `new_tab`, `with_time`, `with_filters` for `DashboardLink` and `url`, `encode`, `new_tab` for `UrlLink`). The markdown needs to be updated to accurately reflect these distinct link types and their specific fields. The current markdown is a simplified representation.
*   **Add `add_link` method documentation:** The `LinksPanel` in `config.py` has an `add_link` method. While this is a method and not a configuration field, it might be useful to mention its existence and purpose in the documentation.

### dashboard_compiler/queries/config.md

*   **No major discrepancies found:** The markdown accurately reflects the `KqlQuery` and `LuceneQuery` types defined in `config.py`.

### dashboard_compiler/dashboard/dashboard.md

*   **Add `data_view` field:** The `Dashboard` in `dashboard/config.py` includes a `data_view` field which is not documented in `dashboard.md`. This field and its description should be added.
*   **Update `settings` field documentation:** The `settings` field in `dashboard/config.py` is a `DashboardSettings` object which includes `margins`, `sync` (DashboardSyncSettings), `controls` (ControlSettings), and `titles`. The markdown currently just lists `settings` as an optional object. The documentation should be updated to detail the fields within `DashboardSettings` and reference the relevant sections for `DashboardSyncSettings` and `ControlSettings`.
*   **Update `controls` field documentation:** The `controls` field in `dashboard/config.py` is a list of `ControlTypes`. The markdown should clarify that this is a list of control objects and refer to the Controls documentation for details on the control types.
*   **Update `panels` field documentation:** The `panels` field in `dashboard/config.py` is a list of `PanelTypes`. The markdown should clarify that this is a list of panel objects and refer to the Panel Object and Panel Types documentation.
*   **Add `add_filter`, `add_control`, `add_panel` method documentation:** The `Dashboard` in `config.py` has `add_filter`, `add_control`, and `add_panel` methods. While these are methods and not configuration fields, it might be useful to mention their existence and purpose in the documentation.

### dashboard_compiler/controls/config.md

*   **Update Control Types:** The `config.py` defines `ControlTypes` as `RangeSliderControl | OptionsListControl | TimeSliderControl`. The markdown needs to be updated to include documentation for the `TimeSliderControl` and its specific fields (`start_offset`, `end_offset`).
*   **Update `ControlSettings` documentation:** The `ControlSettings` in `config.py` includes `label_position`, `apply_global_filters`, `apply_global_timerange`, `ignore_zero_results`, `chain_controls`, and `click_to_apply`. The markdown currently only lists `search_technique` and `sort` under a generic `Controls Configuration` section, which seems incorrect as these are fields of `OptionsListControl`. The markdown needs a dedicated section for `ControlSettings` detailing its fields.
*   **Update `OptionsListControl` fields:** The `OptionsListControl` in `config.py` defines `field`, `fill_width`, `match_technique`, `wait_for_results`, `preselected`, `singular`, and `data_view`. The markdown lists `field`, `data_view`, `search_technique`, and `sort`. The markdown needs to be updated to accurately reflect the fields in `config.py`, including `fill_width`, `match_technique` (with reference to `MatchTechnique` enum), `wait_for_results`, `preselected`, and `singular`. The `sort` field is part of `OptionsListControl` in the markdown but not in the `config.py` model; this needs clarification or correction.
*   **Update `RangeSliderControl` fields:** The `RangeSliderControl` in `config.py` defines `type`, `fill_width`, `field`, `step`, and `data_view`. The markdown lists `type` and `step` under the `Range Slider Control` section, but also mentions common control fields. The markdown should clearly list all fields for `RangeSliderControl`.
*   **Add `MatchTechnique` Enum Documentation:** The `MatchTechnique` enum is defined in `config.py` and used in `OptionsListControl` but not documented. This enum and its values should be documented.
*   **Add `validate_offsets` method documentation:** The `TimeSliderControl` in `config.py` has a `validate_offsets` method. While this is a method and not a configuration field, it might be useful to mention its existence and purpose in the documentation.

## Missing Documentation Files

*   Documentation for chart visualizations defined in `dashboard_compiler/panels/charts/visualizations/config.py`, `dashboard_compiler/panels/charts/visualizations/pie/config.py`, and `dashboard_compiler/panels/charts/visualizations/metric/config.py` is missing. New markdown files should be created to document the configuration for Lens and ESQL Pie and Metric charts.
*   Documentation for the Search Panel (`search.md`) is referenced in `panels/base.md` but the file is missing. A new markdown file should be created to document the Search Panel configuration defined in `dashboard_compiler/panels/search/config.py`.

## Prioritization

The documentation updates should be prioritized as follows:

1.  Address major discrepancies in existing files, such as the incorrect fields in `panels/images/image.md` and the outdated filter and control documentation.
2.  Create missing documentation files for chart visualizations and the Search Panel.
3.  Add missing fields and details to the remaining markdown files.
4.  Ensure consistency in formatting and style across all documentation.

## Next Steps

Assign a Lead Technical Writer to execute this plan by updating the existing markdown files and creating new ones as required.