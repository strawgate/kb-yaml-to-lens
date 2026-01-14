"""Compile sections into their Kibana representations."""

from dashboard_compiler.panels.compile import compile_dashboard_panel, compute_panel_grid
from dashboard_compiler.panels.view import KbnBasePanel, KbnGridData
from dashboard_compiler.sections.config import Section
from dashboard_compiler.sections.view import KbnSection, KbnSectionGridData
from dashboard_compiler.shared.logging import log_compile
from dashboard_compiler.shared.view import KbnReference


@log_compile
def compile_section(section: Section, section_y: int, section_id: str) -> KbnSection:
    """Compile a Section into its Kibana view model representation.

    Args:
        section: The Section object to compile.
        section_y: The calculated y position for the section.
        section_id: The unique identifier for the section.

    Returns:
        KbnSection: The compiled Kibana section view model.

    """
    return KbnSection(
        uid=section_id,
        title=section.title,
        collapsed=section.collapsed if section.collapsed is True else None,
        gridData=KbnSectionGridData(y=section_y),
    )


@log_compile
def compile_section_panels(
    section: Section,
    section_id: str,
) -> tuple[list[KbnReference], list[KbnBasePanel]]:
    """Compile the panels within a section.

    Args:
        section: The Section containing the panels.
        section_id: The ID of the section these panels belong to.

    Returns:
        tuple: A tuple containing the references and compiled panel view models.

    """
    kbn_panels: list[KbnBasePanel] = []
    kbn_references: list[KbnReference] = []

    for panel in section.panels:
        # Compute the grid for each panel
        grid = compute_panel_grid(panel)

        # Compile the panel
        new_references, new_panel = compile_dashboard_panel(panel=panel, grid=grid)

        # Add sectionId to the panel's gridData by creating a new gridData with section_id
        grid_with_section = KbnGridData(
            x=new_panel.gridData.x,
            y=new_panel.gridData.y,
            w=new_panel.gridData.w,
            h=new_panel.gridData.h,
            i=new_panel.gridData.i,
            section_id=section_id,
        )

        # Create a copy of the panel with the updated gridData
        updated_panel = new_panel.model_copy(update={'gridData': grid_with_section})

        kbn_panels.append(updated_panel)
        kbn_references.extend(new_references)

    return kbn_references, kbn_panels
