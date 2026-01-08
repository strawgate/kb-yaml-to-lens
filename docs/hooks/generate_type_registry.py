"""MkDocs hook to generate type registry documentation from Pydantic models."""

import inspect
import logging
import sys
from pathlib import Path
from typing import Any, get_args

from mkdocs.config.defaults import MkDocsConfig

log = logging.getLogger('mkdocs.plugins.type_registry')


def on_pre_build(config: MkDocsConfig, **_kwargs: Any) -> None:
    """Generate type registry documentation before the build starts."""
    # Add compiler source to Python path for imports
    docs_dir = Path(config['docs_dir'])
    repo_root = docs_dir.parent
    compiler_src = repo_root / 'compiler' / 'src'

    if str(compiler_src) not in sys.path:
        sys.path.insert(0, str(compiler_src))

    # Generate the type registry
    generate_type_registry(docs_dir)

    log.info('Generated type registry documentation')


def get_class_description(cls: type) -> str:
    """Extract the first line of a class docstring as its description.

    Args:
        cls: The class to extract documentation from.

    Returns:
        str: The first line of the docstring, or an empty string if none exists.

    """
    if cls.__doc__ is None:
        return ''

    # Get first non-empty line from docstring
    lines = [line.strip() for line in cls.__doc__.strip().split('\n')]
    for line in lines:
        if len(line) > 0:
            return line

    return ''


def get_api_reference_link(cls: type, module_path: str) -> str:
    """Generate a relative link to the API reference for a class.

    Args:
        cls: The class to link to.
        module_path: The module path (e.g., 'dashboard_compiler.panels.types').

    Returns:
        str: A markdown link to the API reference.

    """
    # Map module paths to API reference pages
    module_to_page = {
        'dashboard_compiler.panels.types': 'panels',
        'dashboard_compiler.panels.charts.config': 'panels',
        'dashboard_compiler.panels.charts.lens.metrics.config': 'panels',
        'dashboard_compiler.panels.charts.lens.dimensions.config': 'panels',
        'dashboard_compiler.controls.config': 'controls',
        'dashboard_compiler.filters.config': 'filters',
    }

    page = module_to_page.get(module_path, 'index')
    class_name = cls.__name__

    # Return relative path from docs/_generated/ to api/ pages
    return f'[{class_name}](../api/{page}.md#{module_path.replace(".", "").lower()}.{class_name})'


def extract_panel_types() -> list[dict[str, str]]:
    """Extract panel types from PanelTypes union.

    Returns:
        list: List of dicts with 'name', 'description', and 'link' keys.

    """
    from dashboard_compiler.panels.images import ImagePanel
    from dashboard_compiler.panels.links import LinksPanel
    from dashboard_compiler.panels.markdown import MarkdownPanel
    from dashboard_compiler.panels.charts.config import ESQLPanel, LensPanel
    from dashboard_compiler.panels.search import SearchPanel

    # Manually list panel types since type alias introspection is complex
    panel_classes = [
        MarkdownPanel,
        SearchPanel,
        LinksPanel,
        ImagePanel,
        LensPanel,
        ESQLPanel,
    ]

    types = []
    for panel_cls in panel_classes:
        name = panel_cls.__name__
        description = get_class_description(panel_cls)
        link = get_api_reference_link(panel_cls, 'dashboard_compiler.panels.types')

        types.append({
            'name': name,
            'description': description,
            'link': link,
        })

    return types


def extract_chart_types() -> list[dict[str, str]]:
    """Extract chart types from LensPanelConfig and ESQLPanelConfig unions.

    Returns:
        list: List of dicts with 'name', 'description', and 'link' keys.

    """
    from dashboard_compiler.panels.charts.config import (
        ESQLAreaPanelConfig,
        ESQLBarPanelConfig,
        ESQLDatatablePanelConfig,
        ESQLGaugePanelConfig,
        ESQLHeatmapPanelConfig,
        ESQLLinePanelConfig,
        ESQLMetricPanelConfig,
        ESQLPiePanelConfig,
        ESQLTagcloudPanelConfig,
        LensAreaPanelConfig,
        LensBarPanelConfig,
        LensDatatablePanelConfig,
        LensGaugePanelConfig,
        LensHeatmapPanelConfig,
        LensLinePanelConfig,
        LensMetricPanelConfig,
        LensPiePanelConfig,
        LensTagcloudPanelConfig,
    )

    # Manually list chart config types
    chart_classes = [
        LensMetricPanelConfig,
        LensGaugePanelConfig,
        LensHeatmapPanelConfig,
        LensPiePanelConfig,
        LensLinePanelConfig,
        LensBarPanelConfig,
        LensAreaPanelConfig,
        LensTagcloudPanelConfig,
        LensDatatablePanelConfig,
        ESQLMetricPanelConfig,
        ESQLGaugePanelConfig,
        ESQLHeatmapPanelConfig,
        ESQLPiePanelConfig,
        ESQLLinePanelConfig,
        ESQLBarPanelConfig,
        ESQLAreaPanelConfig,
        ESQLTagcloudPanelConfig,
        ESQLDatatablePanelConfig,
    ]

    types = []
    for chart_cls in chart_classes:
        name = chart_cls.__name__
        description = get_class_description(chart_cls)
        link = get_api_reference_link(chart_cls, 'dashboard_compiler.panels.charts.config')

        types.append({
            'name': name,
            'description': description,
            'link': link,
        })

    return types


def extract_metric_types() -> list[dict[str, str]]:
    """Extract metric types from metric config module.

    Returns:
        list: List of dicts with 'name', 'description', and 'link' keys.

    """
    from dashboard_compiler.panels.charts.lens.metrics.config import (
        LensCountAggregatedMetric,
        LensFormulaMetric,
        LensLastValueAggregatedMetric,
        LensOtherAggregatedMetric,
        LensPercentileAggregatedMetric,
        LensPercentileRankAggregatedMetric,
        LensStaticValue,
        LensSumAggregatedMetric,
    )

    # Manually list metric types
    metric_classes = [
        LensCountAggregatedMetric,
        LensSumAggregatedMetric,
        LensOtherAggregatedMetric,
        LensLastValueAggregatedMetric,
        LensPercentileAggregatedMetric,
        LensPercentileRankAggregatedMetric,
        LensFormulaMetric,
        LensStaticValue,
    ]

    types = []
    for metric_cls in metric_classes:
        name = metric_cls.__name__
        description = get_class_description(metric_cls)
        link = get_api_reference_link(metric_cls, 'dashboard_compiler.panels.charts.lens.metrics.config')

        types.append({
            'name': name,
            'description': description,
            'link': link,
        })

    return types


def extract_dimension_types() -> list[dict[str, str]]:
    """Extract dimension types from dimensions config module.

    Returns:
        list: List of dicts with 'name', 'description', and 'link' keys.

    """
    from dashboard_compiler.panels.charts.lens.dimensions.config import (
        LensDateHistogramDimension,
        LensFiltersDimension,
        LensIntervalsDimension,
        LensTopValuesDimension,
    )

    # Manually list dimension types
    dimension_classes = [
        LensTopValuesDimension,
        LensDateHistogramDimension,
        LensFiltersDimension,
        LensIntervalsDimension,
    ]

    types = []
    for dim_cls in dimension_classes:
        name = dim_cls.__name__
        description = get_class_description(dim_cls)
        link = get_api_reference_link(dim_cls, 'dashboard_compiler.panels.charts.lens.dimensions.config')

        types.append({
            'name': name,
            'description': description,
            'link': link,
        })

    return types


def extract_control_types() -> list[dict[str, str]]:
    """Extract control types from controls config module.

    Returns:
        list: List of dicts with 'name', 'description', and 'link' keys.

    """
    from dashboard_compiler.controls.config import (
        ESQLQueryControl,
        ESQLStaticMultiSelectControl,
        ESQLStaticSingleSelectControl,
        OptionsListControl,
        RangeSliderControl,
        TimeSliderControl,
    )

    # Manually list control types
    control_classes = [
        RangeSliderControl,
        OptionsListControl,
        TimeSliderControl,
        ESQLStaticSingleSelectControl,
        ESQLStaticMultiSelectControl,
        ESQLQueryControl,
    ]

    types = []
    for ctrl_cls in control_classes:
        name = ctrl_cls.__name__
        description = get_class_description(ctrl_cls)
        link = get_api_reference_link(ctrl_cls, 'dashboard_compiler.controls.config')

        types.append({
            'name': name,
            'description': description,
            'link': link,
        })

    return types


def extract_filter_types() -> list[dict[str, str]]:
    """Extract filter types from filters config module.

    Returns:
        list: List of dicts with 'name', 'description', and 'link' keys.

    """
    from dashboard_compiler.filters.config import (
        AndFilter,
        CustomFilter,
        ExistsFilter,
        NegateFilter,
        OrFilter,
        PhraseFilter,
        PhrasesFilter,
        RangeFilter,
    )

    # Manually list filter types
    filter_classes = [
        ExistsFilter,
        PhraseFilter,
        PhrasesFilter,
        RangeFilter,
        CustomFilter,
        AndFilter,
        OrFilter,
        NegateFilter,
    ]

    types = []
    for filter_cls in filter_classes:
        name = filter_cls.__name__
        description = get_class_description(filter_cls)
        link = get_api_reference_link(filter_cls, 'dashboard_compiler.filters.config')

        types.append({
            'name': name,
            'description': description,
            'link': link,
        })

    return types


def format_type_table(types: list[dict[str, str]], section_id: str) -> str:
    """Format a list of types as a markdown table with snippet markers.

    Args:
        types: List of type information dicts.
        section_id: Identifier for the snippet section.

    Returns:
        str: Markdown table string with snippet markers.

    """
    if len(types) == 0:
        return '_No types found._\n'

    lines = [
        f'<!-- --8<-- [start:{section_id}] -->\n',
        '| Type | Description | API Reference |',
        '| ---- | ----------- | ------------- |',
    ]

    for type_info in types:
        lines.append(f"| `{type_info['name']}` | {type_info['description']} | {type_info['link']} |")

    lines.append(f'<!-- --8<-- [end:{section_id}] -->\n')

    return '\n'.join(lines) + '\n'


def generate_type_registry(docs_dir: Path) -> None:
    """Generate the type registry markdown file.

    Args:
        docs_dir: The documentation directory path.

    """
    output_dir = docs_dir / '_generated'
    output_dir.mkdir(exist_ok=True)

    content = ['# Type Registry\n']
    content.append('> Auto-generated from Pydantic model type unions. Do not edit manually.\n')
    content.append('\n')

    # Panel Types
    content.append('## Panel Types\n')
    content.append('\n')
    panel_types = extract_panel_types()
    content.append(format_type_table(panel_types, 'panel-types-table'))
    content.append('\n')

    # Chart Types
    content.append('## Chart Types\n')
    content.append('\n')
    chart_types = extract_chart_types()
    content.append(format_type_table(chart_types, 'chart-types-table'))
    content.append('\n')

    # Metric Types
    content.append('## Metric Types\n')
    content.append('\n')
    metric_types = extract_metric_types()
    content.append(format_type_table(metric_types, 'metric-types-table'))
    content.append('\n')

    # Dimension Types
    content.append('## Dimension Types\n')
    content.append('\n')
    dimension_types = extract_dimension_types()
    content.append(format_type_table(dimension_types, 'dimension-types-table'))
    content.append('\n')

    # Control Types
    content.append('## Control Types\n')
    content.append('\n')
    control_types = extract_control_types()
    content.append(format_type_table(control_types, 'control-types-table'))
    content.append('\n')

    # Filter Types
    content.append('## Filter Types\n')
    content.append('\n')
    filter_types = extract_filter_types()
    content.append(format_type_table(filter_types, 'filter-types-table'))
    content.append('\n')

    output_path = output_dir / 'type_registry.md'
    output_path.write_text(''.join(content), encoding='utf-8')

    log.info(f'Generated {output_path} with {len(panel_types)} panel types, {len(chart_types)} chart types, {len(metric_types)} metric types, {len(dimension_types)} dimension types, {len(control_types)} control types, and {len(filter_types)} filter types')
