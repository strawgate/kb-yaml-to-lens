"""CLI command for upgrading legacy dashboard YAML schema to current format."""

import io
from collections import Counter
from pathlib import Path
from typing import cast

import rich_click as click
from kb_dashboard_core.yaml_roundtrip import dump_roundtrip, load_roundtrip
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from dashboard_compiler.cli_output import print_dim_bullet, print_success, print_warning

YamlMap = CommentedMap
YamlSeq = CommentedSeq

_COMPAT_NOTE = 'Compatibility target: 0.2.7 -> 0.4.0 only (0.3.x compatibility intentionally dropped).'


def _as_map(value: object) -> YamlMap | None:
    return value if isinstance(value, CommentedMap) else None


def _as_seq(value: object) -> YamlSeq | None:
    return value if isinstance(value, CommentedSeq) else None


def _insert_preserving_order(mapping: YamlMap, index: int, key: str, value: object) -> None:
    if key in mapping:
        return
    mapping.insert(index, key, value)


def _rename_key(mapping: YamlMap, old_key: str, new_key: str, stats: Counter[str], stat_name: str) -> None:
    if old_key not in mapping:
        return
    if new_key in mapping:
        stats[f'{stat_name}:skipped'] += 1
        return
    old_index = list(mapping.keys()).index(old_key)
    value = mapping.pop(old_key)
    _insert_preserving_order(mapping, old_index, new_key, value)
    stats[stat_name] += 1


def _ensure_map(parent: YamlMap, key: str) -> YamlMap:
    existing = _as_map(parent.get(key))
    if existing is not None:
        return existing
    created = CommentedMap()
    parent[key] = created
    return created


def _migrate_metric_chart(chart: YamlMap, stats: Counter[str]) -> None:
    chart_color = chart.pop('color', None)
    chart_apply_to = chart.pop('apply_to', None)

    appearance = _as_map(chart.get('appearance'))
    appearance_color_apply_to: object = None
    if appearance is not None:
        appearance_color = _as_map(appearance.get('color'))
        if appearance_color is not None and 'apply_to' in appearance_color:
            appearance_color_apply_to = appearance_color.pop('apply_to')
            if len(appearance_color) == 0:
                appearance.pop('color', None)
            stats['metric:appearance-color-apply-to'] += 1

    primary = _ensure_map(chart, 'primary')
    primary_color = _as_map(primary.get('color'))
    if chart_color is not None:
        if primary_color is None:
            primary['color'] = chart_color
        else:
            stats['metric:chart-color-skipped'] += 1
        stats['metric:chart-color'] += 1

    resolved_apply_to = chart_apply_to if chart_apply_to is not None else appearance_color_apply_to
    if resolved_apply_to is None:
        return

    primary_color = _as_map(primary.get('color'))
    if primary_color is None:
        primary['color'] = CommentedMap({'apply_to': resolved_apply_to})
        stats['metric:apply-to'] += 1
        return

    if 'apply_to' not in primary_color:
        primary_color['apply_to'] = resolved_apply_to
        stats['metric:apply-to'] += 1
    else:
        stats['metric:apply-to-skipped'] += 1


def _collect_datatable_column_configs(columns: YamlSeq | None, metric_columns: YamlSeq | None) -> dict[str, YamlMap]:
    by_column_id: dict[str, YamlMap] = {}
    for group in (columns, metric_columns):
        for col in group or []:
            col_map = _as_map(col)
            if col_map is None:
                continue
            column_id = cast('str | None', col_map.get('column_id'))
            if not isinstance(column_id, str):
                continue
            existing = by_column_id.get(column_id)
            if existing is None:
                by_column_id[column_id] = CommentedMap(col_map)
                continue
            for key, value in col_map.items():
                if key not in existing:
                    existing[key] = value
    return by_column_id


def _apply_metric_column_appearance(metric_map: YamlMap, legacy_col: YamlMap, stats: Counter[str]) -> None:
    appearance = _ensure_map(metric_map, 'appearance')
    for key in ('width', 'hidden', 'alignment', 'summary_row', 'summary_label'):
        if key in legacy_col and key not in appearance:
            appearance[key] = legacy_col[key]
            stats[f'datatable:{key}'] += 1

    color_mode = legacy_col.get('color_mode')
    if color_mode is not None:
        color = _ensure_map(metric_map, 'color')
        if 'apply_to' not in color:
            color['apply_to'] = color_mode
            stats['datatable:color-mode'] += 1


def _apply_breakdown_column_appearance(breakdown_map: YamlMap, legacy_col: YamlMap, stats: Counter[str]) -> None:
    appearance = _ensure_map(breakdown_map, 'appearance')
    for key in ('width', 'hidden', 'alignment'):
        if key in legacy_col and key not in appearance:
            appearance[key] = legacy_col[key]
            stats[f'datatable:{key}'] += 1


def _migrate_datatable_columns(chart: YamlMap, stats: Counter[str]) -> None:
    columns = _as_seq(chart.pop('columns', None))
    metric_columns = _as_seq(chart.pop('metric_columns', None))
    if columns is None and metric_columns is None:
        return

    by_column_id = _collect_datatable_column_configs(columns, metric_columns)

    metrics = _as_seq(chart.get('metrics'))
    if metrics is not None:
        for metric in metrics:
            metric_map = _as_map(metric)
            if metric_map is None:
                continue
            metric_id = cast('str | None', metric_map.get('id'))
            if not isinstance(metric_id, str):
                continue
            legacy_col = by_column_id.get(metric_id)
            if legacy_col is not None:
                _apply_metric_column_appearance(metric_map, legacy_col, stats)

    breakdowns = _as_seq(chart.get('breakdowns'))
    if breakdowns is not None:
        for breakdown in breakdowns:
            breakdown_map = _as_map(breakdown)
            if breakdown_map is None:
                continue
            breakdown_id = cast('str | None', breakdown_map.get('id'))
            if not isinstance(breakdown_id, str):
                continue
            legacy_col = by_column_id.get(breakdown_id)
            if legacy_col is not None:
                _apply_breakdown_column_appearance(breakdown_map, legacy_col, stats)

    stats['datatable:remove-columns'] += 1


def _migrate_heatmap(chart: YamlMap, stats: Counter[str]) -> None:
    grid_config = _as_map(chart.pop('grid_config', None))
    if grid_config is not None:
        appearance = _ensure_map(chart, 'appearance')

        cells = _as_map(grid_config.get('cells'))
        if cells is not None and 'show_labels' in cells:
            values = _ensure_map(appearance, 'values')
            if 'visible' not in values:
                values['visible'] = cells['show_labels']
                stats['heatmap:grid-values-visible'] += 1

        for axis_name in ('x_axis', 'y_axis'):
            legacy_axis = _as_map(grid_config.get(axis_name))
            if legacy_axis is None:
                continue
            axis = _ensure_map(appearance, axis_name)
            if 'show_labels' in legacy_axis:
                labels = _ensure_map(axis, 'labels')
                if 'visible' not in labels:
                    labels['visible'] = legacy_axis['show_labels']
                    stats[f'heatmap:{axis_name}-labels-visible'] += 1
            if 'show_title' in legacy_axis:
                title = _ensure_map(axis, 'title')
                if 'visible' not in title:
                    title['visible'] = legacy_axis['show_title']
                    stats[f'heatmap:{axis_name}-title-visible'] += 1

    legend = _as_map(chart.pop('legend', None))
    if legend is not None:
        appearance = _ensure_map(chart, 'appearance')
        if 'legend' not in appearance:
            appearance['legend'] = legend
            stats['heatmap:legend'] += 1


def _migrate_tagcloud(chart: YamlMap, stats: Counter[str]) -> None:
    appearance = _as_map(chart.get('appearance'))
    if appearance is None or 'show_label' not in appearance:
        return

    show_label = appearance.pop('show_label')
    labels = _as_map(appearance.get('labels'))
    if labels is None:
        appearance['labels'] = CommentedMap({'visible': show_label})
        stats['tagcloud:show-label'] += 1
        return
    if 'visible' not in labels:
        labels['visible'] = show_label
        stats['tagcloud:show-label'] += 1


def _migrate_gauge(chart: YamlMap, stats: Counter[str]) -> None:
    appearance = _as_map(chart.get('appearance'))
    if appearance is None:
        return

    palette = appearance.pop('palette', None)
    if palette is None:
        return
    if 'color' not in chart:
        chart['color'] = palette
        stats['gauge:palette'] += 1
    else:
        stats['gauge:palette-skipped'] += 1


def _normalize_xy_enums(chart: YamlMap, stats: Counter[str]) -> None:
    appearance = _as_map(chart.get('appearance'))
    if appearance is None:
        return
    for key in ('missing_values', 'end_values'):
        value = appearance.get(key)
        if isinstance(value, str):
            lowered = value.lower()
            if lowered != value:
                appearance[key] = lowered
                stats[f'xy:{key}-lowercase'] += 1


def _normalize_legend_visible_bool(legend: YamlMap, stats: Counter[str]) -> None:
    visible = legend.get('visible')
    if isinstance(visible, bool):
        legend['visible'] = 'show' if visible else 'hide'
        stats['legend:visible-bool'] += 1


def _migrate_pie_titles_and_text(chart: YamlMap, stats: Counter[str]) -> None:
    legacy = _as_map(chart.pop('titles_and_text', None))
    if legacy is None:
        return

    appearance = _ensure_map(chart, 'appearance')
    categories = _ensure_map(appearance, 'categories')
    values = _ensure_map(appearance, 'values')

    mappings = (
        ('slice_labels', categories, 'position'),
        ('slice_values', values, 'format'),
        ('value_decimal_places', values, 'decimal_places'),
    )
    for old_key, target, new_key in mappings:
        if old_key in legacy and new_key not in target:
            target[new_key] = legacy[old_key]
            stats['pie:titles-and-text'] += 1


def _strip_legacy_color_continuity(node: YamlMap, stats: Counter[str]) -> None:
    for key in ('continuity', 'extend_beyond_range'):
        if key in node:
            node.pop(key, None)
            stats['color:legacy-continuity'] += 1


def _migrate_dimension_legacy_fields(mapping: YamlMap, stats: Counter[str]) -> None:
    dimension_type = mapping.get('type')
    if dimension_type == 'values':
        _rename_key(mapping, 'other_bucket', 'show_other_bucket', stats, 'dimension:other-bucket')
        _rename_key(mapping, 'missing_bucket', 'include_missing_values', stats, 'dimension:missing-bucket')
    if dimension_type == 'interval':
        _rename_key(mapping, 'empty_bucket', 'include_empty_intervals', stats, 'dimension:empty-bucket')


def _migrate_chart_map(mapping: YamlMap, stats: Counter[str]) -> None:
    chart_type = mapping.get('type')
    if chart_type == 'metric':
        _migrate_metric_chart(mapping, stats)
        return
    if chart_type == 'datatable':
        _rename_key(mapping, 'dimensions', 'breakdowns', stats, 'datatable:dimensions')
        _rename_key(mapping, 'dimensions_by', 'metrics_split_by', stats, 'datatable:dimensions-by')
        _migrate_datatable_columns(mapping, stats)
        return
    if chart_type == 'pie':
        _rename_key(mapping, 'dimensions', 'breakdowns', stats, 'pie:dimensions')
        _migrate_pie_titles_and_text(mapping, stats)
        return
    if chart_type in {'xy', 'line', 'area', 'bar'}:
        _normalize_xy_enums(mapping, stats)
        return
    if chart_type == 'heatmap':
        _migrate_heatmap(mapping, stats)
        return
    if chart_type == 'tagcloud':
        _migrate_tagcloud(mapping, stats)
        return
    if chart_type == 'gauge':
        _migrate_gauge(mapping, stats)


def _visit_node(node: object, stats: Counter[str]) -> None:
    mapping = _as_map(node)
    if mapping is not None:
        _strip_legacy_color_continuity(mapping, stats)
        _migrate_dimension_legacy_fields(mapping, stats)
        legend = _as_map(mapping.get('legend'))
        if legend is not None:
            _rename_key(legend, 'size', 'width', stats, 'legend:size')
            _normalize_legend_visible_bool(legend, stats)
        appearance = _as_map(mapping.get('appearance'))
        if appearance is not None:
            appearance_legend = _as_map(appearance.get('legend'))
            if appearance_legend is not None:
                _normalize_legend_visible_bool(appearance_legend, stats)
        _migrate_chart_map(mapping, stats)

        for value in mapping.values():
            _visit_node(value, stats)
        return

    sequence = _as_seq(node)
    if sequence is not None:
        for item in sequence:
            _visit_node(item, stats)


def _upgrade_document(document: YamlMap) -> Counter[str]:
    stats: Counter[str] = Counter()
    _visit_node(document, stats)
    return stats


def _dump_to_string(document: YamlMap) -> str:
    yaml = YAML(typ='rt')
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    yaml.width = 140
    stream = io.StringIO()
    yaml.dump(document, stream)
    return stream.getvalue()


def _resolve_upgrade_files(input_dir: Path, input_file: Path | None) -> list[Path]:
    if input_file is not None:
        if input_file.suffix != '.yaml':
            msg = f'Input file must have a .yaml extension: {input_file}'
            raise click.ClickException(msg)
        return [input_file]
    if input_dir.is_dir() is False:
        msg = f'Directory not found: {input_dir}'
        raise click.ClickException(msg)
    files = sorted(input_dir.rglob('*.yaml'))
    if len(files) == 0:
        msg = f'No YAML files found in {input_dir}'
        raise click.ClickException(msg)
    return files


def _upgrade_file(yaml_file: Path, write: bool) -> bool:
    try:
        original_content = yaml_file.read_text(encoding='utf-8')
        document = load_roundtrip(str(yaml_file))
        stats = _upgrade_document(document)
        upgraded_content = _dump_to_string(document)
    except (OSError, TypeError, ValueError) as e:
        msg = f'Error upgrading {yaml_file}: {e}'
        raise click.ClickException(msg) from e

    if stats.total() == 0 or upgraded_content == original_content:
        return False

    if write:
        try:
            dump_roundtrip(document, str(yaml_file))
        except OSError as e:
            msg = f'Error upgrading {yaml_file}: {e}'
            raise click.ClickException(msg) from e
        print_success(f'Upgraded {yaml_file}')
        print_dim_bullet(f'{stats.total()} change(s) applied')
    else:
        print_warning(f'Upgrade needed: {yaml_file}')
        print_dim_bullet(f'{stats.total()} change(s) would be applied')
    return True


@click.command('upgrade')
@click.option(
    '--input-dir',
    type=click.Path(file_okay=False, path_type=Path),
    default=Path('inputs'),
    show_default=True,
    help='Directory containing dashboard YAML files.',
)
@click.option(
    '--input-file',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help='Single YAML dashboard file to upgrade. When provided, --input-dir is ignored.',
)
@click.option(
    '--write',
    is_flag=True,
    default=False,
    help='Write changes in-place. Without this flag, runs in check mode.',
)
@click.option(
    '--fail-on-change',
    is_flag=True,
    default=False,
    help='Exit with non-zero status if upgrades are needed.',
)
def upgrade_dashboards(input_dir: Path, input_file: Path | None, write: bool, fail_on_change: bool) -> None:
    """Upgrade dashboard YAML schema from 0.2.7 to 0.4.0.

    This command only targets the 0.2.7 -> 0.4.0 migration path.
    0.3.x compatibility is intentionally not preserved.
    """
    files = _resolve_upgrade_files(input_dir=input_dir, input_file=input_file)

    changed_files = 0
    for yaml_file in files:
        if _upgrade_file(yaml_file=yaml_file, write=write):
            changed_files += 1

    if changed_files == 0:
        print_success('No upgrades needed.')
        print_dim_bullet(_COMPAT_NOTE)
        return

    mode_label = 'updated' if write else 'would be updated'
    print_success(f'{changed_files} file(s) {mode_label}.')
    print_dim_bullet(_COMPAT_NOTE)
    if write is False:
        print_dim_bullet('Re-run with --write to apply changes.')

    if fail_on_change:
        raise SystemExit(min(changed_files, 125))
