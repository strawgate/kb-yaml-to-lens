"""Phase 2: Infer Dashboard config objects from parsed intermediate structures.

Maps parsed Kibana/Kbn view data to actual kb-dashboard-core config models.
"""

from typing import Any

from kb_dashboard_core.dashboard.config import Dashboard

from .parse import (
    ParsedColumn,
    ParsedControl,
    ParsedDashboard,
    ParsedESQLColumn,
    ParsedESQLLayer,
    ParsedFilter,
    ParsedFormLayer,
    ParsedLensPanel,
    ParsedPanel,
    ParsedSimplePanel,
    ParsedVisualizationLayerRole,
    ParsedVisualizationState,
    as_dict,
)
from .tables import (
    CONTROL_TYPE_MAP,
    LENS_VISUALIZATION_TYPES,
    OPERATION_TYPE_MAP,
    PIE_SHAPES,
    SKIP_OPERATION_TYPES,
    XY_SERIES_TYPES,
    XY_STACKING_MODES,
)

# ---------------------------------------------------------------------------
# Chart type resolution
# ---------------------------------------------------------------------------


def _resolve_chart_type(vis_state: ParsedVisualizationState) -> str | None:
    raw = vis_state.raw_type
    if raw is None:
        return None
    normalized = LENS_VISUALIZATION_TYPES.get(raw.lower())
    if raw.lower() in {'lnsxy', 'xy'}:
        pst = vis_state.preferred_series_type
        if pst is not None:
            return XY_SERIES_TYPES.get(pst, 'line')
        return 'line'
    if raw.lower() in {'lnspie', 'pie'}:
        shape = vis_state.shape
        if shape is not None:
            resolved = PIE_SHAPES.get(shape)
            if resolved is not None and resolved != 'pie':
                return resolved
    return normalized


def _resolve_stacking_mode(vis_state: ParsedVisualizationState, chart_type: str | None) -> str | None:
    if chart_type not in {'bar', 'area'}:
        return None
    pst = vis_state.preferred_series_type
    if pst is None:
        return None
    return XY_STACKING_MODES.get(pst)


# ---------------------------------------------------------------------------
# Metric / dimension / breakdown extraction (form-based)
# ---------------------------------------------------------------------------


def _extract_metric_filter(col: ParsedColumn) -> dict[str, str] | None:
    if col.filter_query is not None:
        if col.filter_language == 'kuery':
            return {'kql': col.filter_query}
        if col.filter_language == 'lucene':
            return {'lucene': col.filter_query}
    kql = col.params.get('kql')
    if isinstance(kql, str) and len(kql) > 0:
        return {'kql': kql}
    return None


def _extract_metric_format(col: ParsedColumn) -> dict[str, Any] | None:
    format_config = as_dict(col.params.get('format'))
    if format_config is None:
        return None
    format_type = format_config.get('id')
    if not (isinstance(format_type, str) and format_type in {'number', 'bytes', 'bits', 'percent', 'duration', 'custom'}):
        return None
    fmt: dict[str, Any] = {'type': format_type}
    format_params = as_dict(format_config.get('params'))
    if format_params is None:
        return fmt
    for key in ('decimals', 'suffix', 'compact', 'pattern'):
        val = format_params.get(key)
        if val is not None:
            fmt[key] = val
    return fmt


def _build_metric_dict(col: ParsedColumn) -> dict[str, Any] | None:
    """Build a metric config dict from a form-based column. Returns None if skipped."""
    if col.operation_type in SKIP_OPERATION_TYPES:
        return None
    aggregation = OPERATION_TYPE_MAP.get(col.operation_type)
    if aggregation is None:
        return None

    metric: dict[str, Any] = {'aggregation': aggregation}
    if col.source_field is not None and col.source_field != 'Records':
        metric['field'] = col.source_field
    if col.label is not None and len(col.label) > 0:
        metric['label'] = col.label
    filt = _extract_metric_filter(col)
    if filt is not None:
        metric['filter'] = filt
    fmt = _extract_metric_format(col)
    if fmt is not None:
        metric['format'] = fmt
    return metric


def _build_dimension_dict(col: ParsedColumn) -> tuple[str, dict[str, Any]] | None:
    """Build a dimension or breakdown dict. Returns (category, dict) or None."""
    if col.operation_type == 'date_histogram':
        dim: dict[str, Any] = {'type': 'date_histogram'}
        if col.source_field is not None:
            dim['field'] = col.source_field
        interval = col.params.get('interval')
        if isinstance(interval, str) and interval != 'auto':
            dim['minimum_interval'] = interval
        return 'dimension', dim

    if col.operation_type == 'terms':
        bd: dict[str, Any] = {'type': 'values'}
        if col.source_field is not None:
            bd['field'] = col.source_field
        size = col.params.get('size')
        if isinstance(size, int):
            bd['size'] = size
        return 'breakdown', bd

    if col.operation_type == 'filters':
        filters_list: list[dict[str, Any]] = []
        raw_filters = col.params.get('filters')
        if isinstance(raw_filters, list):
            for f in raw_filters:  # pyright: ignore[reportUnknownVariableType]
                if isinstance(f, dict):
                    f_entry: dict[str, Any] = {}
                    label = f.get('label')  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
                    if isinstance(label, str):
                        f_entry['label'] = label
                    inp = f.get('input')  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
                    if isinstance(inp, dict):
                        query = inp.get('query')  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
                        language = inp.get('language')  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
                        if isinstance(query, str):
                            if language == 'lucene':
                                f_entry['query'] = {'lucene': query}
                            else:
                                f_entry['query'] = {'kql': query}
                    if 'query' in f_entry:
                        filters_list.append(f_entry)
        if not filters_list:
            filters_list = [{'query': {'kql': '*'}}]
        return 'breakdown', {'type': 'filters', 'filters': filters_list}

    return None


def _classify_form_columns(
    layer: ParsedFormLayer,
    layer_role: ParsedVisualizationLayerRole | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """Classify form-based columns into metrics, dimensions, breakdowns, skipped."""
    metrics: list[dict[str, Any]] = []
    dimensions: list[dict[str, Any]] = []
    breakdowns: list[dict[str, Any]] = []
    skipped: list[str] = []

    # Determine iteration order: prefer visualization accessor order
    if layer_role is not None and layer_role.accessors:
        ordered_ids = list(dict.fromkeys([*layer_role.accessors, *layer.column_order, *list(layer.columns.keys())]))
    elif layer.column_order:
        ordered_ids = layer.column_order
    else:
        ordered_ids = list(layer.columns.keys())

    for col_id in ordered_ids:
        col = layer.columns.get(col_id)
        if col is None:
            continue
        if col.is_bucketed:
            result = _build_dimension_dict(col)
            if result is not None:
                category, stub = result
                if category == 'dimension':
                    dimensions.append(stub)
                else:
                    breakdowns.append(stub)
        else:
            metric = _build_metric_dict(col)
            if metric is not None:
                metrics.append(metric)
            elif col.operation_type in SKIP_OPERATION_TYPES:
                skipped.append(col.operation_type)
            else:
                skipped.append(col.operation_type)

    return metrics, dimensions, breakdowns, skipped


# ---------------------------------------------------------------------------
# ES|QL column extraction
# ---------------------------------------------------------------------------


def _classify_esql_columns(
    layer: ParsedESQLLayer,
    layer_role: ParsedVisualizationLayerRole | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Classify ES|QL columns into metrics, dimensions, breakdowns using layer roles."""
    metrics: list[dict[str, Any]] = []
    dimensions: list[dict[str, Any]] = []
    breakdowns: list[dict[str, Any]] = []

    columns_by_id: dict[str, ParsedESQLColumn] = {c.column_id: c for c in layer.columns}

    if layer_role is None:
        return metrics, dimensions, breakdowns

    for metric_id in layer_role.metric_ids:
        col = columns_by_id.get(metric_id)
        if col is None:
            continue
        m: dict[str, Any] = {'field': col.field_name}
        if col.label is not None and col.label != col.field_name:
            m['label'] = col.label
        metrics.append(m)

    if layer_role.dimension_id is not None:
        col = columns_by_id.get(layer_role.dimension_id)
        if col is not None:
            d: dict[str, Any] = {'field': col.field_name}
            if col.label is not None and col.label != col.field_name:
                d['label'] = col.label
            dimensions.append(d)

    if layer_role.breakdown_id is not None:
        col = columns_by_id.get(layer_role.breakdown_id)
        if col is not None:
            b: dict[str, Any] = {'field': col.field_name}
            if col.label is not None and col.label != col.field_name:
                b['label'] = col.label
            breakdowns.append(b)

    return metrics, dimensions, breakdowns


# ---------------------------------------------------------------------------
# Panel inference
# ---------------------------------------------------------------------------


def _infer_lens_chart(parsed: ParsedLensPanel) -> dict[str, Any]:
    """Build chart config dict from a parsed Lens/ES|QL panel."""
    chart: dict[str, Any] = {}
    vis_state = parsed.visualization_state

    # Resolve chart type
    chart_type: str | None = None
    if vis_state is not None:
        chart_type = _resolve_chart_type(vis_state)
        if chart_type is not None:
            chart['type'] = chart_type
            mode = _resolve_stacking_mode(vis_state, chart_type)
            if mode is not None:
                chart['mode'] = mode
            # Donut detection
            if chart_type == 'pie' and vis_state.shape == 'donut':
                chart.setdefault('appearance', {})['donut'] = 'medium'
    if chart_type is None:
        chart_type = 'metric'
        chart['type'] = chart_type

    # Data view / query
    if parsed.panel_type == 'lens' and parsed.data_view_id is not None:
        chart['data_view'] = parsed.data_view_id

    esql_query: str | None = None
    if parsed.panel_type == 'esql':
        # Check top-level query first, then layer queries
        esql_query = parsed.esql_query
        if esql_query is None:
            for layer in parsed.esql_layers.values():
                esql_query = layer.query
                break
        chart['query'] = esql_query if esql_query is not None else 'TODO_esql_query'

    # Extract metrics/dimensions/breakdowns
    all_metrics: list[dict[str, Any]] = []
    all_dimensions: list[dict[str, Any]] = []
    all_breakdowns: list[dict[str, Any]] = []
    has_skipped_metrics = False

    if parsed.panel_type == 'esql':
        for layer_id, layer in parsed.esql_layers.items():
            role = vis_state.layer_roles.get(layer_id) if vis_state else None
            m, d, b = _classify_esql_columns(layer, role)
            all_metrics.extend(m)
            all_dimensions.extend(d)
            all_breakdowns.extend(b)
    else:
        for layer_id, layer in parsed.form_layers.items():
            role = vis_state.layer_roles.get(layer_id) if vis_state else None
            m, d, b, skipped = _classify_form_columns(layer, role)
            all_metrics.extend(m)
            all_dimensions.extend(d)
            all_breakdowns.extend(b)
            if skipped:
                has_skipped_metrics = True

    # Assign metrics/dimensions/breakdowns based on chart type
    is_xy = chart_type in {'line', 'bar', 'area'}
    is_metric_chart = chart_type == 'metric'
    is_singular_metric = chart_type in {'gauge', 'tagcloud', 'waffle', 'mosaic'}
    is_singular_dim = chart_type in {'tagcloud', 'waffle', 'mosaic'}
    is_heatmap = chart_type == 'heatmap'
    is_partition = chart_type in {'pie', 'treemap'}
    uses_plural_metrics = chart_type in {'pie', 'treemap', 'datatable'} or is_xy

    default_lens_metric: dict[str, Any] = {'aggregation': 'count'}
    unsupported_lens_metric: dict[str, Any] = {
        'aggregation': 'sum',
        'field': 'TODO_unsupported_metric_field',
        'label': 'TODO_unsupported_metric',
    }
    default_esql_metric: dict[str, Any] = {'field': 'TODO_metric_field'}
    default_lens_dim: dict[str, Any] = {'type': 'values', 'field': 'TODO_field'}
    default_esql_dim: dict[str, Any] = {'field': 'TODO_dimension_field'}

    # -- Metrics assignment --
    if is_metric_chart:
        if len(all_metrics) > 0:
            chart['primary'] = all_metrics[0]
        if len(all_metrics) > 1:
            chart['secondary'] = all_metrics[1]
    elif is_heatmap:
        if len(all_metrics) > 0:
            chart['value'] = all_metrics[0]
    elif is_singular_metric:
        # gauge, tagcloud, waffle, mosaic use singular 'metric'
        if len(all_metrics) > 0:
            chart['metric'] = all_metrics[0]
    elif uses_plural_metrics and len(all_metrics) > 0:
        chart['metrics'] = all_metrics

    # -- Dimensions assignment --
    if is_xy:
        if len(all_dimensions) > 0:
            chart['dimension'] = all_dimensions[0]
        if len(all_breakdowns) > 0:
            chart['breakdown'] = all_breakdowns[0]
    elif is_heatmap:
        if len(all_dimensions) > 0:
            chart['x_axis'] = all_dimensions[0]
        if len(all_breakdowns) > 0:
            chart['y_axis'] = all_breakdowns[0]
        elif len(all_dimensions) > 1:
            chart['y_axis'] = all_dimensions[1]
    elif is_singular_dim:
        # tagcloud, waffle use singular 'dimension'
        merged = [*all_dimensions, *all_breakdowns]
        if len(merged) > 0:
            chart['dimension'] = merged[0]
        if chart_type == 'mosaic' and len(merged) > 1:
            chart['breakdown'] = merged[1]
    else:
        merged = [*all_dimensions, *all_breakdowns]
        if len(merged) > 0:
            chart['dimensions'] = merged

    # Fill in required defaults for incomplete panels
    is_lens = parsed.panel_type == 'lens'
    if is_lens:
        lens_metric_fallback = unsupported_lens_metric if has_skipped_metrics else default_lens_metric
        if 'data_view' not in chart:
            chart['data_view'] = 'TODO_data_view'
        if is_metric_chart and 'primary' not in chart:
            chart['primary'] = lens_metric_fallback
        if is_xy and 'metrics' not in chart:
            chart['metrics'] = [lens_metric_fallback]
        if is_partition:
            if 'metrics' not in chart:
                chart['metrics'] = [lens_metric_fallback]
            if 'dimensions' not in chart:
                chart['dimensions'] = [default_lens_dim]
        if chart_type == 'datatable' and 'metrics' not in chart and 'dimensions' not in chart:
            chart['metrics'] = [lens_metric_fallback]
        if is_heatmap:
            if 'x_axis' not in chart:
                chart['x_axis'] = default_lens_dim
            if 'value' not in chart:
                chart['value'] = lens_metric_fallback
        if is_singular_metric and 'metric' not in chart:
            chart['metric'] = lens_metric_fallback
        if is_singular_dim and 'dimension' not in chart:
            chart['dimension'] = default_lens_dim
    else:
        if is_metric_chart and 'primary' not in chart:
            chart['primary'] = default_esql_metric
        if is_xy and 'metrics' not in chart:
            chart['metrics'] = [default_esql_metric]
        if is_partition:
            if 'metrics' not in chart:
                chart['metrics'] = [default_esql_metric]
            if 'dimensions' not in chart:
                chart['dimensions'] = [default_esql_dim]
        if chart_type == 'datatable' and 'metrics' not in chart and 'dimensions' not in chart:
            chart['metrics'] = [default_esql_metric]
        if is_heatmap:
            if 'x_axis' not in chart:
                chart['x_axis'] = default_esql_dim
            if 'value' not in chart:
                chart['value'] = default_esql_metric
        if is_singular_metric and 'metric' not in chart:
            chart['metric'] = default_esql_metric
        if is_singular_dim and 'dimension' not in chart:
            chart['dimension'] = default_esql_dim

    return chart


def _infer_markdown_panel(simple: ParsedSimplePanel, _ref_lookup: dict[str, str]) -> dict[str, Any]:
    """Infer markdown panel config from parsed simple panel."""
    config: dict[str, Any] = {}
    ec = simple.embeddable_config

    content = ec.get('markdown')
    if not isinstance(content, str):
        saved_vis = as_dict(ec.get('savedVis'))
        if saved_vis is not None:
            params = as_dict(saved_vis.get('params'))
            if params is not None:
                content = params.get('markdown')

    config['content'] = content if isinstance(content, str) else 'TODO(decompile): provide markdown content'

    saved_vis = as_dict(ec.get('savedVis'))
    if saved_vis is not None:
        params = as_dict(saved_vis.get('params'))
        if params is not None:
            font_size = params.get('fontSize')
            if isinstance(font_size, int):
                config['font_size'] = font_size
            links_in_new_tab = params.get('openLinksInNewTab')
            if isinstance(links_in_new_tab, bool):
                config['links_in_new_tab'] = links_in_new_tab

    return config


def _infer_search_panel(simple: ParsedSimplePanel, ref_lookup: dict[str, str]) -> dict[str, Any]:
    """Infer search panel config from parsed simple panel."""
    panel = simple.raw
    saved_search_id = panel.get('savedSearchId')
    if isinstance(saved_search_id, str):
        return {'saved_search_id': saved_search_id}

    ec = as_dict(panel.get('embeddableConfig'))
    if ec is not None:
        ref_name = ec.get('savedSearchRefName')
        if isinstance(ref_name, str):
            resolved = ref_lookup.get(ref_name)
            if isinstance(resolved, str):
                return {'saved_search_id': resolved}

    return {'saved_search_id': 'TODO_saved_search_id'}


def _infer_image_panel(simple: ParsedSimplePanel, _ref_lookup: dict[str, str]) -> dict[str, Any]:
    """Infer image panel config from parsed simple panel."""
    config: dict[str, Any] = {}
    ec = simple.embeddable_config

    image_config = as_dict(ec.get('imageConfig'))
    if image_config is not None:
        src = as_dict(image_config.get('src'))
        if src is not None:
            url = src.get('url')
            if isinstance(url, str):
                config['from_url'] = url
        sizing = as_dict(image_config.get('sizing'))
        if sizing is not None:
            fit = sizing.get('objectFit')
            if isinstance(fit, str) and fit in {'contain', 'cover', 'fill', 'none'}:
                config['fit'] = fit
        alt = image_config.get('altText')
        if isinstance(alt, str) and len(alt) > 0:
            config['description'] = alt
        bg = image_config.get('backgroundColor')
        if isinstance(bg, str) and len(bg) > 0:
            config['background_color'] = bg

    if 'from_url' not in config:
        config['from_url'] = 'TODO_image_url'
    return config


def _build_link_common(raw_link: dict[str, Any]) -> dict[str, Any]:
    item: dict[str, Any] = {}
    link_id = raw_link.get('id')
    if isinstance(link_id, str):
        item['id'] = link_id
    label = raw_link.get('label')
    if isinstance(label, str):
        item['label'] = label
    return item


def _infer_links_panel(simple: ParsedSimplePanel, ref_lookup: dict[str, str]) -> dict[str, Any]:
    """Infer links panel config from parsed simple panel."""
    attrs = simple.embeddable_attributes
    if not attrs:
        attrs = as_dict(simple.embeddable_config.get('attributes')) or {}

    config: dict[str, Any] = {}
    layout = attrs.get('layout')
    if isinstance(layout, str) and layout in {'horizontal', 'vertical'}:
        config['layout'] = layout

    items: list[dict[str, Any]] = []
    raw_links = attrs.get('links')
    if isinstance(raw_links, list):
        for raw_item in raw_links:  # pyright: ignore[reportUnknownVariableType]
            raw_link = as_dict(raw_item)  # pyright: ignore[reportUnknownArgumentType]
            if raw_link is None:
                continue
            options = as_dict(raw_link.get('options')) or {}
            link_type = raw_link.get('type')

            if link_type == 'externalLink':
                dest = raw_link.get('destination')
                if not isinstance(dest, str):
                    continue
                item = _build_link_common(raw_link)
                item['url'] = dest
                new_tab = options.get('openInNewTab')
                if isinstance(new_tab, bool):
                    item['new_tab'] = new_tab
                encode = options.get('encodeUrl')
                if isinstance(encode, bool):
                    item['encode'] = encode
                items.append(item)

            elif link_type == 'dashboardLink':
                dest_ref = raw_link.get('destinationRefName')
                if not isinstance(dest_ref, str):
                    continue
                item = _build_link_common(raw_link)
                dashboard_id = ref_lookup.get(dest_ref)
                item['dashboard'] = dashboard_id if isinstance(dashboard_id, str) else f'TODO_dashboard_id_for_{dest_ref}'
                new_tab = options.get('openInNewTab')
                if isinstance(new_tab, bool):
                    item['new_tab'] = new_tab
                with_time = options.get('useCurrentDateRange')
                if isinstance(with_time, bool):
                    item['with_time'] = with_time
                with_filters = options.get('useCurrentFilters')
                if isinstance(with_filters, bool):
                    item['with_filters'] = with_filters
                items.append(item)

    config['items'] = items
    return config


def _infer_vega_panel(_simple: ParsedSimplePanel, _ref_lookup: dict[str, str]) -> dict[str, Any]:
    return {'spec': {}}


# ---------------------------------------------------------------------------
# Dashboard-level inference
# ---------------------------------------------------------------------------


def _infer_settings(parsed: ParsedDashboard) -> dict[str, Any] | None:
    s = parsed.settings
    if s is None:
        return None
    settings: dict[str, Any] = {}
    sync: dict[str, Any] = {}
    if s.margins is not None:
        settings['margins'] = s.margins
    if s.sync_colors is not None:
        sync['colors'] = s.sync_colors
    if s.sync_cursor is not None:
        sync['cursor'] = s.sync_cursor
    if s.sync_tooltips is not None:
        sync['tooltips'] = s.sync_tooltips
    if sync:
        settings['sync'] = sync
    if s.hide_panel_titles is not None:
        settings['titles'] = not s.hide_panel_titles
    return settings if settings else None


def _infer_time_range(parsed: ParsedDashboard) -> dict[str, str] | None:
    if parsed.time_from is None and parsed.time_to is None:
        return None
    tr: dict[str, str] = {}
    if parsed.time_from is not None:
        tr['from'] = parsed.time_from
    if parsed.time_to is not None:
        tr['to'] = parsed.time_to
    return tr


def _infer_filter(pf: ParsedFilter) -> dict[str, Any]:
    """Infer a single filter config dict."""
    f: dict[str, Any] = {}
    if pf.filter_type == 'exists':
        f['exists'] = pf.key
    elif pf.filter_type == 'phrase':
        f['field'] = pf.key
        params = pf.meta.get('params')
        if isinstance(params, dict):
            query = params.get('query')  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType]
            if isinstance(query, (str, int, float, bool)):
                f['equals'] = query
        else:
            value = pf.meta.get('value')
            if isinstance(value, (str, int, float, bool)):
                f['equals'] = value
    elif pf.filter_type == 'phrases':
        f['field'] = pf.key
        params = pf.meta.get('params')
        if isinstance(params, list):
            f['in'] = [p for p in params if isinstance(p, (str, int, float, bool))]  # pyright: ignore[reportUnknownVariableType]
    elif pf.filter_type == 'range':
        f['field'] = pf.key
        range_params = as_dict(pf.raw.get('range'))
        if range_params is not None:
            field_range = as_dict(range_params.get(pf.key))
            if field_range is not None:
                for bound in ('gte', 'gt', 'lte', 'lt'):
                    val = field_range.get(bound)
                    if isinstance(val, (str, int, float, bool)):
                        f[bound] = val
    else:
        f['field'] = pf.key

    # Apply metadata
    disabled = pf.meta.get('disabled')
    if isinstance(disabled, bool) and disabled:
        f['disabled'] = True
    alias = pf.meta.get('alias')
    if isinstance(alias, str) and len(alias) > 0:
        f['alias'] = alias

    return f


def _infer_control(pc: ParsedControl) -> dict[str, Any]:
    """Infer a single control config dict."""
    ctrl: dict[str, Any] = {}
    if pc.control_type is not None:
        ctrl['type'] = CONTROL_TYPE_MAP.get(pc.control_type, f'TODO_control_type_{pc.control_type}')
    else:
        ctrl['type'] = 'TODO_control_type_unknown'
    if pc.field_name is not None:
        ctrl['field'] = pc.field_name
    if pc.title is not None:
        ctrl['label'] = pc.title
    # data_view is required for options and range controls
    resolved_type = ctrl.get('type')
    if resolved_type in {'options', 'range'}:
        ctrl['data_view'] = pc.data_view_id if pc.data_view_id is not None else 'TODO_data_view'
    elif pc.data_view_id is not None:
        ctrl['data_view'] = pc.data_view_id
    return ctrl


def _infer_panel(panel: ParsedPanel, ref_lookup: dict[str, str]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Infer panel config. Returns (panel_type_key, chart_config_dict, panel_wrapper_dict).

    The panel_wrapper_dict contains id, title, size, position.
    The chart_config_dict is nested under the panel_type_key.
    """
    wrapper: dict[str, Any] = {}
    if panel.panel_index is not None:
        wrapper['id'] = panel.panel_index
    wrapper['title'] = panel.title

    if panel.grid is not None:
        g = panel.grid
        if g.w is not None or g.h is not None:
            size: dict[str, int] = {}
            if g.w is not None:
                size['w'] = g.w
            if g.h is not None:
                size['h'] = g.h
            wrapper['size'] = size
        if g.x is not None or g.y is not None:
            pos: dict[str, int] = {}
            if g.x is not None:
                pos['x'] = g.x
            if g.y is not None:
                pos['y'] = g.y
            wrapper['position'] = pos

    # Error fallback
    if panel.error is not None:
        return 'markdown', {'content': f'TODO(decompile): {panel.error}'}, wrapper

    # Lens/ESQL panel
    if panel.lens is not None:
        chart = _infer_lens_chart(panel.lens)
        return panel.lens.panel_type, chart, wrapper

    # Simple panels
    if panel.simple is not None:
        simple_builders: dict[str, Any] = {
            'markdown': _infer_markdown_panel,
            'search': _infer_search_panel,
            'links': _infer_links_panel,
            'image': _infer_image_panel,
            'vega': _infer_vega_panel,
        }
        builder = simple_builders.get(panel.simple.panel_type)
        if builder is not None:
            config = builder(panel.simple, ref_lookup)  # pyright: ignore[reportAny]
            return panel.simple.panel_type, config, wrapper
        # Unsupported type
        return 'markdown', {'content': f'TODO(decompile): unsupported panel type `{panel.simple.panel_type}`'}, wrapper

    return 'markdown', {'content': 'TODO(decompile): empty panel'}, wrapper


def infer_dashboard(parsed: ParsedDashboard) -> tuple[Dashboard, list[dict[str, Any]]]:
    """Infer a Dashboard config model from parsed dashboard data.

    Returns:
        Tuple of (dashboard_model, panel_originals) where dashboard_model is an
        actual ``kb_dashboard_core.dashboard.config.Dashboard`` instance.
    """
    dashboard: dict[str, Any] = {
        'name': parsed.title,
    }
    if parsed.dashboard_id is not None:
        dashboard['id'] = parsed.dashboard_id
    if parsed.description is not None:
        dashboard['description'] = parsed.description

    settings = _infer_settings(parsed)
    if settings is not None:
        dashboard['settings'] = settings

    time_range = _infer_time_range(parsed)
    if time_range is not None:
        dashboard['time_range'] = time_range

    if parsed.filters:
        dashboard['filters'] = [_infer_filter(f) for f in parsed.filters]

    if parsed.controls:
        dashboard['controls'] = [_infer_control(c) for c in parsed.controls]

    if parsed.query is not None:
        dashboard['query'] = parsed.query

    panels: list[dict[str, Any]] = []
    for panel in parsed.panels:
        panel_type, chart_config, wrapper = _infer_panel(panel, parsed.reference_lookup)
        wrapper[panel_type] = chart_config
        panels.append(wrapper)

    dashboard['panels'] = panels
    return Dashboard.model_validate(dashboard), []
