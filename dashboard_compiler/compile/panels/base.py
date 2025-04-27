from dashboard_compiler.compile.utils import stable_id_generator
from dashboard_compiler.models.config.panels.markdown import MarkdownPanel
from dashboard_compiler.models.views.base import KbnGridData


def compile_panel_shared(panel: MarkdownPanel) -> tuple[str, KbnGridData]:
    panel_index = panel.id or stable_id_generator([panel.type, panel.title, str(panel.grid)])

    grid_data = KbnGridData(x=panel.grid.x, y=panel.grid.y, w=panel.grid.w, h=panel.grid.h, i=panel_index)

    return panel_index, grid_data
