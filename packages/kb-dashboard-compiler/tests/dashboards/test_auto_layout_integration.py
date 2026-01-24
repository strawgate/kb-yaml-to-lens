"""Integration tests for auto-layout with dashboards."""

import pytest

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.compile import compile_dashboard_panels
from dashboard_compiler.panels.markdown.config import MarkdownPanel


class TestAutoLayoutIntegration:
    """Integration tests for auto-layout functionality."""

    def test_panels_with_no_position_get_auto_positioned(self) -> None:
        """Test that panels without position are automatically positioned during compilation."""
        dashboard = Dashboard(
            name='Auto Layout Test',
            panels=[
                MarkdownPanel(title='Panel 1', markdown={'content': 'Test 1'}),
                MarkdownPanel(title='Panel 2', markdown={'content': 'Test 2'}),
            ],
        )

        # Grid positions should be calculated during compilation
        _, kbn_panels = compile_dashboard_panels(dashboard.panels)

        assert kbn_panels[0].gridData.x == 0
        assert kbn_panels[0].gridData.y == 0
        assert kbn_panels[1].gridData.x == 12  # Default width is now 12
        assert kbn_panels[1].gridData.y == 0

    def test_panels_use_default_size(self) -> None:
        """Test that panels without size use default 12w x 8h."""
        dashboard = Dashboard(
            name='Default Size Test',
            panels=[
                MarkdownPanel(title='Panel 1', markdown={'content': 'Test'}),
            ],
        )

        _, kbn_panels = compile_dashboard_panels(dashboard.panels)

        assert kbn_panels[0].gridData.w == 12
        assert kbn_panels[0].gridData.h == 8

    def test_panels_with_semantic_width(self) -> None:
        """Test panels using semantic width values."""
        dashboard = Dashboard(
            name='Semantic Width Test',
            panels=[
                MarkdownPanel(title='Quarter', size={'w': 'quarter'}, markdown={'content': 'Q'}),
                MarkdownPanel(title='Half', size={'w': 'half'}, markdown={'content': 'H'}),
                MarkdownPanel(title='Whole', size={'w': 'whole'}, markdown={'content': 'W'}),
            ],
        )

        _, kbn_panels = compile_dashboard_panels(dashboard.panels)

        assert kbn_panels[0].gridData.w == 12
        assert kbn_panels[1].gridData.w == 24
        assert kbn_panels[2].gridData.w == 48

    def test_four_panels_form_grid(self) -> None:
        """Test that four default panels form a 4-panel row (4 x 12-wide panels)."""
        dashboard = Dashboard(
            name='Grid Test',
            panels=[MarkdownPanel(title=f'Panel {i}', markdown={'content': f'Test {i}'}) for i in range(4)],
        )

        _, kbn_panels = compile_dashboard_panels(dashboard.panels)

        # Default width is 12, so 4 panels fit in one row (4 * 12 = 48)
        assert kbn_panels[0].gridData.x == 0
        assert kbn_panels[0].gridData.y == 0
        assert kbn_panels[1].gridData.x == 12
        assert kbn_panels[1].gridData.y == 0
        assert kbn_panels[2].gridData.x == 24
        assert kbn_panels[2].gridData.y == 0
        assert kbn_panels[3].gridData.x == 36
        assert kbn_panels[3].gridData.y == 0

    def test_locked_and_auto_panels_mixed(self) -> None:
        """Test mixing locked and auto-positioned panels."""
        dashboard = Dashboard(
            name='Mixed Layout Test',
            panels=[
                MarkdownPanel(
                    title='Locked',
                    position={'x': 0, 'y': 0},
                    size={'w': 24, 'h': 20},
                    markdown={'content': 'Locked'},
                ),
                MarkdownPanel(title='Auto 1', markdown={'content': 'Auto 1'}),
                MarkdownPanel(title='Auto 2', markdown={'content': 'Auto 2'}),
            ],
        )

        _, kbn_panels = compile_dashboard_panels(dashboard.panels)

        assert kbn_panels[0].gridData.x == 0
        assert kbn_panels[0].gridData.y == 0
        # Auto panels flow to the right of the locked panel (which is 24 wide)
        assert kbn_panels[1].gridData.x == 24
        assert kbn_panels[1].gridData.y == 0
        assert kbn_panels[2].gridData.x == 36  # Next panel at 24 + 12 = 36
        assert kbn_panels[2].gridData.y == 0

    def test_full_width_panel_then_auto_panels(self) -> None:
        """Test full-width panel followed by auto-positioned panels."""
        dashboard = Dashboard(
            name='Full Width Test',
            panels=[
                MarkdownPanel(
                    title='Header',
                    size={'w': 'whole', 'h': 8},
                    markdown={'content': 'Header'},
                ),
                MarkdownPanel(title='Panel 1', markdown={'content': 'P1'}),
                MarkdownPanel(title='Panel 2', markdown={'content': 'P2'}),
            ],
        )

        _, kbn_panels = compile_dashboard_panels(dashboard.panels)

        assert kbn_panels[0].gridData.x == 0
        assert kbn_panels[0].gridData.y == 0
        assert kbn_panels[0].gridData.w == 48
        assert kbn_panels[1].gridData.x == 0
        assert kbn_panels[1].gridData.y == 8
        assert kbn_panels[2].gridData.x == 12  # Default width is 12, not 24
        assert kbn_panels[2].gridData.y == 8

    def test_overlapping_panels_raises_error(self) -> None:
        """Test that manually overlapping panels raise validation error during compilation."""
        dashboard = Dashboard(
            name='Overlap Test',
            panels=[
                MarkdownPanel(
                    title='Panel 1',
                    position={'x': 0, 'y': 0},
                    size={'w': 30, 'h': 15},
                    markdown={'content': 'P1'},
                ),
                MarkdownPanel(
                    title='Panel 2',
                    position={'x': 20, 'y': 10},
                    size={'w': 20, 'h': 15},
                    markdown={'content': 'P2'},
                ),
            ],
        )

        with pytest.raises(ValueError, match='overlaps with'):
            compile_dashboard_panels(dashboard.panels)

    def test_panels_with_custom_sizes(self) -> None:
        """Test panels with various custom sizes."""
        dashboard = Dashboard(
            name='Custom Sizes Test',
            panels=[
                MarkdownPanel(
                    title='Third',
                    size={'w': 'third', 'h': 10},
                    markdown={'content': 'T'},
                ),
                MarkdownPanel(
                    title='Third 2',
                    size={'w': 'third', 'h': 10},
                    markdown={'content': 'T2'},
                ),
                MarkdownPanel(
                    title='Third 3',
                    size={'w': 'third', 'h': 10},
                    markdown={'content': 'T3'},
                ),
            ],
        )

        _, kbn_panels = compile_dashboard_panels(dashboard.panels)

        assert kbn_panels[0].gridData.w == 16
        assert kbn_panels[0].gridData.x == 0
        assert kbn_panels[1].gridData.w == 16
        assert kbn_panels[1].gridData.x == 16
        assert kbn_panels[2].gridData.w == 16
        assert kbn_panels[2].gridData.x == 32

    def test_size_and_position_field_aliases(self) -> None:
        """Test that field aliases work for size and position."""
        dashboard = Dashboard(
            name='Alias Test',
            panels=[
                MarkdownPanel(
                    title='Alias Test',
                    size={'width': 20, 'height': 10},
                    position={'from_left': 5, 'from_top': 3},
                    markdown={'content': 'Test'},
                ),
            ],
        )

        _, kbn_panels = compile_dashboard_panels(dashboard.panels)

        assert kbn_panels[0].gridData.x == 5
        assert kbn_panels[0].gridData.y == 3
        assert kbn_panels[0].gridData.w == 20
        assert kbn_panels[0].gridData.h == 10

    def test_eighth_width_panels_fit_in_row(self) -> None:
        """Test that eight eighth-width panels fit in one row."""
        dashboard = Dashboard(
            name='Eighth Width Test',
            panels=[
                MarkdownPanel(
                    title=f'Panel {i}',
                    size={'w': 'eighth', 'h': 10},
                    markdown={'content': f'P{i}'},
                )
                for i in range(8)
            ],
        )

        _, kbn_panels = compile_dashboard_panels(dashboard.panels)

        for i, kbn_panel in enumerate(kbn_panels):
            assert kbn_panel.gridData.x == i * 6
            assert kbn_panel.gridData.y == 0
            assert kbn_panel.gridData.w == 6
