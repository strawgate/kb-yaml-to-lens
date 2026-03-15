"""Compare disassembled dashboard directories for round-trip validation."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PanelInfo:
    """Panel metadata extracted from a disassembled dashboard panel file."""

    filename: str
    panel_type: str
    title: str


@dataclass(frozen=True)
class PanelComparison:
    """Comparison result for a panel index between original and compiled dashboards."""

    index: int
    original: PanelInfo | None
    compiled: PanelInfo | None

    @property
    def types_match(self) -> bool:
        """Whether panel types match when both panel entries exist."""
        if self.original is None or self.compiled is None:
            return False
        return self.original.panel_type == self.compiled.panel_type


@dataclass(frozen=True)
class DashboardComparison:
    """Aggregate comparison results for two disassembled dashboard directories."""

    original_count: int
    compiled_count: int
    panels: list[PanelComparison]

    @property
    def matching_panel_types(self) -> int:
        """Count panel positions where both panel types match."""
        return sum(1 for panel in self.panels if panel.types_match)

    @property
    def all_panels_match(self) -> bool:
        """True when panel count and panel types match at every index."""
        return self.original_count == self.compiled_count and self.matching_panel_types == self.original_count


def get_panel_info(disassembled_dir: Path) -> list[PanelInfo]:
    """Extract panel information from a disassembled dashboard directory."""
    panels_dir = disassembled_dir / 'panels'
    if not panels_dir.is_dir():
        msg = f'Panels directory not found: {panels_dir}'
        raise FileNotFoundError(msg)

    panels: list[PanelInfo] = []
    for panel_file in sorted(panels_dir.iterdir()):
        if not panel_file.is_file():
            continue
        with panel_file.open(encoding='utf-8') as f:
            panel: dict[str, Any] = json.load(f)  # pyright: ignore[reportAny]
        panel_type: str = panel.get('type', 'unknown')  # pyright: ignore[reportAny]
        panel_config: dict[str, Any] | None = panel.get('panelConfig')
        fallback_title: str = panel_config.get('title', '(no title)') if panel_config is not None else '(no title)'
        title: str = panel.get('title', fallback_title)  # pyright: ignore[reportAny]
        panels.append(PanelInfo(filename=panel_file.name, panel_type=panel_type, title=title))
    return panels


def compare_disassembled_dashboards(original_dir: Path, compiled_dir: Path) -> DashboardComparison:
    """Compare panel structures from original and compiled disassembled dashboards."""
    original_panels = get_panel_info(original_dir)
    compiled_panels = get_panel_info(compiled_dir)

    panel_comparisons: list[PanelComparison] = []
    max_panels = max(len(original_panels), len(compiled_panels))
    for index in range(max_panels):
        original_panel = original_panels[index] if index < len(original_panels) else None
        compiled_panel = compiled_panels[index] if index < len(compiled_panels) else None
        panel_comparisons.append(
            PanelComparison(
                index=index,
                original=original_panel,
                compiled=compiled_panel,
            )
        )

    return DashboardComparison(
        original_count=len(original_panels),
        compiled_count=len(compiled_panels),
        panels=panel_comparisons,
    )
