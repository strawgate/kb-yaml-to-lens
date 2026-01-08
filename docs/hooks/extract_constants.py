"""MkDocs hook to extract constants from source code for documentation."""

import logging
import sys
from pathlib import Path
from typing import Any

from mkdocs.config.defaults import MkDocsConfig

log = logging.getLogger('mkdocs.plugins.extract_constants')


def on_pre_build(config: MkDocsConfig, **_kwargs: Any) -> None:
    """Extract constants before the build starts."""
    # Add compiler source to Python path for imports
    docs_dir = Path(config['docs_dir'])
    repo_root = docs_dir.parent
    compiler_src = repo_root / 'compiler' / 'src'

    if str(compiler_src) not in sys.path:
        sys.path.insert(0, str(compiler_src))

    # Generate the constants documentation
    generate_constants(docs_dir)

    log.info('Generated constants documentation')


def generate_constants(docs_dir: Path) -> None:
    """Generate the constants markdown file.

    Args:
        docs_dir: The documentation directory path.

    """
    from dashboard_compiler.panels.config import (
        GRID_WIDTH_EIGHTH,
        GRID_WIDTH_HALF,
        GRID_WIDTH_QUARTER,
        GRID_WIDTH_SIXTH,
        GRID_WIDTH_THIRD,
        GRID_WIDTH_WHOLE,
    )

    output_dir = docs_dir / '_generated'
    output_dir.mkdir(exist_ok=True)

    content = ['# Constants\n']
    content.append('> Auto-generated from source code constants. Do not edit manually.\n')
    content.append('\n')

    # Semantic Width Constants
    content.append('## Semantic Width Constants\n')
    content.append('\n')
    content.append('The following semantic width values are available for panel sizing:\n')
    content.append('\n')

    # Create the table with snippet markers
    semantic_widths = [
        ('whole', GRID_WIDTH_WHOLE, 'Full dashboard width'),
        ('half', GRID_WIDTH_HALF, 'Half width'),
        ('third', GRID_WIDTH_THIRD, 'One-third width'),
        ('quarter', GRID_WIDTH_QUARTER, 'Quarter width'),
        ('sixth', GRID_WIDTH_SIXTH, 'One-sixth width'),
        ('eighth', GRID_WIDTH_EIGHTH, 'One-eighth width'),
    ]

    content.append('<!-- --8<-- [start:semantic-width-constants-table] -->\n')
    content.append('| Semantic Value | Grid Units | Description |\n')
    content.append('| -------------- | ---------- | ----------- |\n')

    for semantic_name, grid_units, description in semantic_widths:
        content.append(f'| `{semantic_name}` | {grid_units} | {description} |\n')

    content.append('<!-- --8<-- [end:semantic-width-constants-table] -->\n')
    content.append('\n')

    output_path = output_dir / 'constants.md'
    output_path.write_text(''.join(content), encoding='utf-8')

    log.info(f'Generated {output_path} with {len(semantic_widths)} semantic width constants')
