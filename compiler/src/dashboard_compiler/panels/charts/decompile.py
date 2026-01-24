"""Decompile Kibana Lens chart panels back to config models."""

from typing import Any

from dashboard_compiler.panels.types import PanelTypes
from dashboard_compiler.shared.decompile import ReferenceResolver
from dashboard_compiler.shared.decompile_context import DecompileContext


def get_layer_id(viz_state: dict[str, Any]) -> str | None:
    """Extract the primary layer ID from visualization state.

    Args:
        viz_state: The visualization state dict.

    Returns:
        The layer ID, or None if not found.

    """
    # Most visualizations have a 'layers' array or 'layerId' field
    if 'layerId' in viz_state:
        return viz_state['layerId']
    if 'layers' in viz_state and len(viz_state['layers']) > 0:
        first_layer = viz_state['layers'][0]
        if isinstance(first_layer, dict):
            return first_layer.get('layerId')
    return None


def get_data_view_from_references(
    references: list[dict[str, Any]],
    layer_id: str | None,
) -> str:
    """Extract data view ID from references for a given layer.

    Args:
        references: List of reference objects.
        layer_id: The layer ID to find the data view for.

    Returns:
        The data view ID string.

    """
    if layer_id is None:
        # Find any index-pattern reference
        for ref in references:
            if ref.get('type') == 'index-pattern':
                return ref.get('id', '')
        return ''

    # Look for reference matching the layer
    ref_name = f'indexpattern-datasource-layer-{layer_id}'
    for ref in references:
        if ref.get('name') == ref_name:
            return ref.get('id', '')

    # Fallback to first index-pattern
    for ref in references:
        if ref.get('type') == 'index-pattern':
            return ref.get('id', '')
    return ''


def decompile_esql_chart(
    kbn_panel: dict[str, Any],
    viz_type: str,
    *,
    context: DecompileContext,
) -> PanelTypes | None:
    """Decompile an ES|QL-based chart panel.

    Args:
        kbn_panel: The Kibana panel dict.
        viz_type: The visualization type.
        context: Decompilation context for warnings.

    Returns:
        The decompiled ESQLPanel config, or None if unsupported.

    Note:
        This is a basic implementation that extracts chart type and query.
        Full metric/dimension extraction requires additional implementation.
        Currently returns None and warns about incomplete decompilation.

    """
    embeddable_config = kbn_panel.get('embeddableConfig', {})
    attributes = embeddable_config.get('attributes', {})
    title = attributes.get('title', '')

    # For now, warn that full ES|QL chart decompilation is not yet complete
    context.warn(
        f'ES|QL {viz_type} chart decompilation not yet fully implemented - requires manual metric/dimension configuration',
        panel_title=title,
    )
    return None


def decompile_lens_chart(
    kbn_panel: dict[str, Any],
    viz_type: str,
    *,
    context: DecompileContext,
    reference_resolver: ReferenceResolver,  # noqa: ARG001
) -> PanelTypes | None:
    """Decompile a form-based (data view) Lens chart panel.

    Args:
        kbn_panel: The Kibana panel dict.
        viz_type: The visualization type.
        context: Decompilation context for warnings.
        reference_resolver: Resolver for panel references.

    Returns:
        The decompiled LensPanel config, or None if unsupported.

    Note:
        This is a basic implementation that extracts chart type and data view.
        Full metric/dimension extraction requires additional implementation.
        Currently returns None and warns about incomplete decompilation.

    """
    embeddable_config = kbn_panel.get('embeddableConfig', {})
    attributes = embeddable_config.get('attributes', {})
    title = attributes.get('title', '')

    # For now, warn that full Lens chart decompilation is not yet complete
    context.warn(
        f'Lens {viz_type} chart decompilation not yet fully implemented - requires manual metric/dimension configuration',
        panel_title=title,
    )
    return None


def decompile_lens_panel(
    kbn_panel: dict[str, Any],
    *,
    context: DecompileContext,
    reference_resolver: ReferenceResolver,
) -> PanelTypes | None:
    """Decompile a Kibana Lens panel to config model.

    Args:
        kbn_panel: The Kibana panel dict.
        context: Decompilation context for warnings.
        reference_resolver: Resolver for panel references.

    Returns:
        The decompiled panel config, or None if unsupported.

    """
    embeddable_config = kbn_panel.get('embeddableConfig', {})
    attributes = embeddable_config.get('attributes', {})
    viz_type = attributes.get('visualizationType', 'unknown')
    state = attributes.get('state', {})
    datasource = state.get('datasourceStates', {})

    # Determine if this is ES|QL or form-based
    text_based = datasource.get('textBased', {})
    text_layers = text_based.get('layers', {}) if text_based else {}

    if text_layers and len(text_layers) > 0:
        # ES|QL-based chart
        return decompile_esql_chart(kbn_panel, viz_type, context=context)
    # Form-based (data view) chart
    return decompile_lens_chart(
        kbn_panel,
        viz_type,
        context=context,
        reference_resolver=reference_resolver,
    )
