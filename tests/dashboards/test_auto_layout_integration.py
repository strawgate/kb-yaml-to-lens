"""Integration tests for auto-layout with dashboards."""

import pytest
from pydantic import ValidationError

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.markdown.config import MarkdownPanel


class TestAutoLayoutIntegration:
    """Integration tests for auto-layout functionality."""

    def test_panels_with_no_position_get_auto_positioned(self) -> None:
        """Test that panels without position are automatically positioned."""
        dashboard = Dashboard(
            name='Auto Layout Test',
            panels=[
                MarkdownPanel(title='Panel 1', markdown={'content': 'Test 1'}),
                MarkdownPanel(title='Panel 2', markdown={'content': 'Test 2'}),
            ],
        )

        assert dashboard.panels[0].grid is not None
        assert dashboard.panels[0].grid.x == 0
        assert dashboard.panels[0].grid.y == 0
        assert dashboard.panels[1].grid is not None
        assert dashboard.panels[1].grid.x == 24
        assert dashboard.panels[1].grid.y == 0

    def test_panels_use_default_size(self) -> None:
        """Test that panels without size use default 24w x 12h."""
        dashboard = Dashboard(
            name='Default Size Test',
            panels=[
                MarkdownPanel(title='Panel 1', markdown={'content': 'Test'}),
            ],
        )

        assert dashboard.panels[0].grid.w == 24
        assert dashboard.panels[0].grid.h == 12

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

        assert dashboard.panels[0].grid.w == 12
        assert dashboard.panels[1].grid.w == 24
        assert dashboard.panels[2].grid.w == 48

    def test_four_panels_form_grid(self) -> None:
        """Test that four default panels form a 2x2 grid."""
        dashboard = Dashboard(
            name='Grid Test',
            panels=[MarkdownPanel(title=f'Panel {i}', markdown={'content': f'Test {i}'}) for i in range(4)],
        )

        assert dashboard.panels[0].grid.x == 0
        assert dashboard.panels[0].grid.y == 0
        assert dashboard.panels[1].grid.x == 24
        assert dashboard.panels[1].grid.y == 0
        assert dashboard.panels[2].grid.x == 0
        assert dashboard.panels[2].grid.y == 12
        assert dashboard.panels[3].grid.x == 24
        assert dashboard.panels[3].grid.y == 12

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

        assert dashboard.panels[0].grid.x == 0
        assert dashboard.panels[0].grid.y == 0
        assert dashboard.panels[1].grid.x == 24
        assert dashboard.panels[1].grid.y == 0
        assert dashboard.panels[2].grid.x == 24
        assert dashboard.panels[2].grid.y == 12

    def test_legacy_grid_field_still_works(self) -> None:
        """Test that legacy grid field still works for backward compatibility."""
        dashboard = Dashboard(
            name='Legacy Grid Test',
            panels=[
                MarkdownPanel(
                    title='Legacy',
                    grid={'x': 10, 'y': 5, 'w': 20, 'h': 15},
                    markdown={'content': 'Test'},
                ),
            ],
        )

        assert dashboard.panels[0].grid.x == 10
        assert dashboard.panels[0].grid.y == 5
        assert dashboard.panels[0].grid.w == 20
        assert dashboard.panels[0].grid.h == 15

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

        assert dashboard.panels[0].grid.x == 0
        assert dashboard.panels[0].grid.y == 0
        assert dashboard.panels[0].grid.w == 48
        assert dashboard.panels[1].grid.x == 0
        assert dashboard.panels[1].grid.y == 8
        assert dashboard.panels[2].grid.x == 24
        assert dashboard.panels[2].grid.y == 8

    def test_overlapping_panels_raises_error(self) -> None:
        """Test that manually overlapping panels still raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            _ = Dashboard(
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
        assert 'overlaps with' in str(exc_info.value)

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

        assert dashboard.panels[0].grid.w == 16
        assert dashboard.panels[0].grid.x == 0
        assert dashboard.panels[1].grid.w == 16
        assert dashboard.panels[1].grid.x == 16
        assert dashboard.panels[2].grid.w == 16
        assert dashboard.panels[2].grid.x == 32

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

        assert dashboard.panels[0].grid.x == 5
        assert dashboard.panels[0].grid.y == 3
        assert dashboard.panels[0].grid.w == 20
        assert dashboard.panels[0].grid.h == 10

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

        for i, panel in enumerate(dashboard.panels):
            assert panel.grid.x == i * 6
            assert panel.grid.y == 0
            assert panel.grid.w == 6
