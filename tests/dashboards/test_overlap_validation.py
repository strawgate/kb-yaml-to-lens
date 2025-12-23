"""Test dashboard panel overlap validation."""

import pytest
from pydantic import ValidationError

from dashboard_compiler.dashboard.config import Dashboard
from dashboard_compiler.panels.config import Grid
from dashboard_compiler.panels.markdown.config import MarkdownPanel


def test_dashboard_no_overlap():
    """Test that non-overlapping panels are accepted."""
    panel1 = MarkdownPanel(
        grid=Grid(x=0, y=0, w=24, h=10),
        type='markdown',
        content='Panel 1',
    )
    panel2 = MarkdownPanel(
        grid=Grid(x=0, y=10, w=24, h=10),
        type='markdown',
        content='Panel 2',
    )
    dashboard = Dashboard(
        name='Test Dashboard',
        panels=[panel1, panel2],
    )
    assert len(dashboard.panels) == 2


def test_dashboard_adjacent_panels_horizontal():
    """Test that horizontally adjacent panels (touching but not overlapping) are accepted."""
    panel1 = MarkdownPanel(
        grid=Grid(x=0, y=0, w=12, h=10),
        type='markdown',
        content='Left Panel',
    )
    panel2 = MarkdownPanel(
        grid=Grid(x=12, y=0, w=12, h=10),
        type='markdown',
        content='Right Panel',
    )
    dashboard = Dashboard(
        name='Test Dashboard',
        panels=[panel1, panel2],
    )
    assert len(dashboard.panels) == 2


def test_dashboard_adjacent_panels_vertical():
    """Test that vertically adjacent panels (touching but not overlapping) are accepted."""
    panel1 = MarkdownPanel(
        grid=Grid(x=0, y=0, w=24, h=10),
        type='markdown',
        content='Top Panel',
    )
    panel2 = MarkdownPanel(
        grid=Grid(x=0, y=10, w=24, h=10),
        type='markdown',
        content='Bottom Panel',
    )
    dashboard = Dashboard(
        name='Test Dashboard',
        panels=[panel1, panel2],
    )
    assert len(dashboard.panels) == 2


def test_dashboard_overlap_complete():
    """Test that completely overlapping panels are detected."""
    panel1 = MarkdownPanel(
        grid=Grid(x=0, y=0, w=24, h=10),
        type='markdown',
        title='First Panel',
        content='Panel 1',
    )
    panel2 = MarkdownPanel(
        grid=Grid(x=0, y=0, w=24, h=10),
        type='markdown',
        title='Second Panel',
        content='Panel 2',
    )
    with pytest.raises(ValidationError) as exc_info:
        Dashboard(
            name='Test Dashboard',
            panels=[panel1, panel2],
        )
    error_msg = str(exc_info.value)
    assert 'overlaps with' in error_msg
    assert 'First Panel' in error_msg
    assert 'Second Panel' in error_msg


def test_dashboard_overlap_partial():
    """Test that partially overlapping panels are detected."""
    panel1 = MarkdownPanel(
        grid=Grid(x=0, y=0, w=20, h=10),
        type='markdown',
        title='Panel A',
        content='Panel 1',
    )
    panel2 = MarkdownPanel(
        grid=Grid(x=10, y=5, w=20, h=10),
        type='markdown',
        title='Panel B',
        content='Panel 2',
    )
    with pytest.raises(ValidationError) as exc_info:
        Dashboard(
            name='Test Dashboard',
            panels=[panel1, panel2],
        )
    error_msg = str(exc_info.value)
    assert 'overlaps with' in error_msg
    assert 'Panel A' in error_msg
    assert 'Panel B' in error_msg


def test_dashboard_overlap_contained():
    """Test that a panel completely inside another is detected as overlapping."""
    panel1 = MarkdownPanel(
        grid=Grid(x=0, y=0, w=48, h=30),
        type='markdown',
        title='Large Panel',
        content='Large Panel',
    )
    panel2 = MarkdownPanel(
        grid=Grid(x=10, y=10, w=10, h=5),
        type='markdown',
        title='Small Panel',
        content='Small Panel',
    )
    with pytest.raises(ValidationError) as exc_info:
        Dashboard(
            name='Test Dashboard',
            panels=[panel1, panel2],
        )
    error_msg = str(exc_info.value)
    assert 'overlaps with' in error_msg
    assert 'Large Panel' in error_msg
    assert 'Small Panel' in error_msg


def test_dashboard_overlap_edge_case_same_x():
    """Test overlap when panels share the same x coordinate but overlap in y."""
    panel1 = MarkdownPanel(
        grid=Grid(x=0, y=0, w=24, h=10),
        type='markdown',
        title='Top Panel',
        content='Panel 1',
    )
    panel2 = MarkdownPanel(
        grid=Grid(x=0, y=5, w=24, h=10),
        type='markdown',
        title='Overlapping Panel',
        content='Panel 2',
    )
    with pytest.raises(ValidationError) as exc_info:
        Dashboard(
            name='Test Dashboard',
            panels=[panel1, panel2],
        )
    error_msg = str(exc_info.value)
    assert 'overlaps with' in error_msg


def test_dashboard_no_overlap_different_rows():
    """Test that panels in different rows don't overlap."""
    panel1 = MarkdownPanel(
        grid=Grid(x=0, y=0, w=48, h=10),
        type='markdown',
        content='Row 1',
    )
    panel2 = MarkdownPanel(
        grid=Grid(x=0, y=10, w=48, h=10),
        type='markdown',
        content='Row 2',
    )
    panel3 = MarkdownPanel(
        grid=Grid(x=0, y=20, w=48, h=10),
        type='markdown',
        content='Row 3',
    )
    dashboard = Dashboard(
        name='Test Dashboard',
        panels=[panel1, panel2, panel3],
    )
    assert len(dashboard.panels) == 3


def test_dashboard_no_overlap_grid_layout():
    """Test a typical grid layout with multiple panels that don't overlap."""
    panels = [
        MarkdownPanel(grid=Grid(x=0, y=0, w=12, h=10), type='markdown', content='Panel 1'),
        MarkdownPanel(grid=Grid(x=12, y=0, w=12, h=10), type='markdown', content='Panel 2'),
        MarkdownPanel(grid=Grid(x=24, y=0, w=12, h=10), type='markdown', content='Panel 3'),
        MarkdownPanel(grid=Grid(x=36, y=0, w=12, h=10), type='markdown', content='Panel 4'),
        MarkdownPanel(grid=Grid(x=0, y=10, w=24, h=15), type='markdown', content='Panel 5'),
        MarkdownPanel(grid=Grid(x=24, y=10, w=24, h=15), type='markdown', content='Panel 6'),
    ]
    dashboard = Dashboard(
        name='Test Dashboard',
        panels=panels,
    )
    assert len(dashboard.panels) == 6


def test_dashboard_overlap_error_message_format():
    """Test that overlap error message includes helpful grid position information."""
    panel1 = MarkdownPanel(
        grid=Grid(x=5, y=10, w=20, h=15),
        type='markdown',
        title='First',
        content='Panel 1',
    )
    panel2 = MarkdownPanel(
        grid=Grid(x=15, y=15, w=20, h=15),
        type='markdown',
        title='Second',
        content='Panel 2',
    )
    with pytest.raises(ValidationError) as exc_info:
        Dashboard(
            name='Test Dashboard',
            panels=[panel1, panel2],
        )
    error_msg = str(exc_info.value)
    # Check that grid coordinates are included
    assert 'x=5' in error_msg
    assert 'y=10' in error_msg
    assert 'w=20' in error_msg
    assert 'h=15' in error_msg
    assert 'x=15' in error_msg
    assert 'y=15' in error_msg
