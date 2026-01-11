"""Fixture generator integration for pytest.

This module provides utilities to invoke the TypeScript fixture generator
directly from pytest, allowing both YAML definitions and LensConfigBuilder
configurations to be defined in the same test function.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

# Project paths
_TESTS_DIR = Path(__file__).parent.parent
_COMPILER_DIR = _TESTS_DIR.parent
_PROJECT_ROOT = _COMPILER_DIR.parent
_FIXTURE_GEN_DIR = _PROJECT_ROOT / 'fixture-generator'

# Docker image configuration
DEFAULT_KIBANA_VERSION = 'v9.2.0'
DEFAULT_BASE_IMAGE = 'ghcr.io/strawgate/kb-yaml-to-lens/kibana-base'


def docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    else:
        return result.returncode == 0


def fixture_image_available(kibana_version: str = DEFAULT_KIBANA_VERSION) -> bool:
    """Check if the fixture generator Docker image is available locally."""
    image_name = f'{DEFAULT_BASE_IMAGE}:{kibana_version}'
    try:
        result = subprocess.run(
            ['docker', 'images', '-q', image_name],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    else:
        return bool(result.stdout.strip())


def pull_fixture_image(kibana_version: str = DEFAULT_KIBANA_VERSION) -> bool:
    """Pull the fixture generator Docker image from GHCR."""
    image_name = f'{DEFAULT_BASE_IMAGE}:{kibana_version}'
    try:
        result = subprocess.run(
            ['docker', 'pull', image_name],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes for large image
            check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    else:
        return result.returncode == 0


# Chart type literals
ChartType = Literal['metric', 'xy', 'pie', 'gauge', 'heatmap', 'tagcloud', 'treemap', 'waffle', 'datatable']


@dataclass
class TimeRange:
    """Time range configuration for fixtures."""

    from_: str = 'now-24h'
    to: str = 'now'
    type: str = 'relative'

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for TypeScript."""
        return {'from': self.from_, 'to': self.to, 'type': self.type}


@dataclass
class LensDataset:
    """Dataset configuration for LensConfigBuilder."""

    esql: str | None = None
    index: str | None = None
    time_field_name: str | None = None

    def to_ts(self) -> str:
        """Convert to TypeScript object literal."""
        if self.esql is not None:
            return f'{{ esql: {json.dumps(self.esql)} }}'
        if self.index is not None:
            parts = [f'index: {json.dumps(self.index)}']
            if self.time_field_name is not None:
                parts.append(f'timeFieldName: {json.dumps(self.time_field_name)}')
            return '{ ' + ', '.join(parts) + ' }'
        msg = 'Dataset must have either esql or index'
        raise ValueError(msg)


@dataclass
class LensMetricConfig:
    """Configuration for metric chart."""

    title: str
    dataset: LensDataset
    value: str
    label: str | None = None

    def to_ts(self) -> str:
        """Convert to TypeScript LensMetricConfig."""
        lines = [
            "chartType: 'metric'",
            f'title: {json.dumps(self.title)}',
            f'dataset: {self.dataset.to_ts()}',
            f'value: {json.dumps(self.value)}',
        ]
        if self.label is not None:
            lines.append(f'label: {json.dumps(self.label)}')
        return '{\n    ' + ',\n    '.join(lines) + '\n  }'


@dataclass
class LensPieConfig:
    """Configuration for pie chart."""

    title: str
    dataset: LensDataset
    value: str
    breakdown: list[str]
    legend_show: bool = True
    legend_position: str = 'right'

    def to_ts(self) -> str:
        """Convert to TypeScript LensPieConfig."""
        lines = [
            "chartType: 'pie'",
            f'title: {json.dumps(self.title)}',
            f'dataset: {self.dataset.to_ts()}',
            f'value: {json.dumps(self.value)}',
            f'breakdown: {json.dumps(self.breakdown)}',
            f'legend: {{ show: {"true" if self.legend_show else "false"}, position: {json.dumps(self.legend_position)} }}',
        ]
        return '{\n    ' + ',\n    '.join(lines) + '\n  }'


@dataclass
class LensXYLayer:
    """Configuration for XY chart layer."""

    type: str = 'series'
    series_type: str = 'line'
    x_axis: str | dict[str, Any] | None = None
    y_axis: list[dict[str, Any]] = field(default_factory=list)

    def to_ts(self) -> str:
        """Convert to TypeScript layer object."""
        lines = [
            f'type: {json.dumps(self.type)}',
            f'seriesType: {json.dumps(self.series_type)}',
        ]
        if self.x_axis is not None:
            if isinstance(self.x_axis, str):
                lines.append(f'xAxis: {json.dumps(self.x_axis)}')
            else:
                lines.append(f'xAxis: {json.dumps(self.x_axis)}')
        if self.y_axis:
            y_items = [json.dumps(y) for y in self.y_axis]
            lines.append(f'yAxis: [{", ".join(y_items)}]')
        return '{\n      ' + ',\n      '.join(lines) + '\n    }'


@dataclass
class LensXYConfig:
    """Configuration for XY chart."""

    title: str
    dataset: LensDataset
    layers: list[LensXYLayer]
    legend_show: bool = True
    legend_position: str = 'right'

    def to_ts(self) -> str:
        """Convert to TypeScript LensXYConfig."""
        layers_ts = ', '.join(layer.to_ts() for layer in self.layers)
        lines = [
            "chartType: 'xy'",
            f'title: {json.dumps(self.title)}',
            f'dataset: {self.dataset.to_ts()}',
            f'layers: [{layers_ts}]',
            f'legend: {{ show: {"true" if self.legend_show else "false"}, position: {json.dumps(self.legend_position)} }}',
        ]
        return '{\n    ' + ',\n    '.join(lines) + '\n  }'


@dataclass
class LensGaugeConfig:
    """Configuration for gauge chart."""

    title: str
    dataset: LensDataset
    value: str
    query_min_value: str | None = None
    query_max_value: str | None = None
    query_goal_value: str | None = None
    shape: str = 'arc'

    def to_ts(self) -> str:
        """Convert to TypeScript LensGaugeConfig."""
        lines = [
            "chartType: 'gauge'",
            f'title: {json.dumps(self.title)}',
            f'dataset: {self.dataset.to_ts()}',
            f'value: {json.dumps(self.value)}',
            f'shape: {json.dumps(self.shape)}',
        ]
        if self.query_min_value is not None:
            lines.append(f'queryMinValue: {json.dumps(self.query_min_value)}')
        if self.query_max_value is not None:
            lines.append(f'queryMaxValue: {json.dumps(self.query_max_value)}')
        if self.query_goal_value is not None:
            lines.append(f'queryGoalValue: {json.dumps(self.query_goal_value)}')
        return '{\n    ' + ',\n    '.join(lines) + '\n  }'


@dataclass
class LensHeatmapConfig:
    """Configuration for heatmap chart."""

    title: str
    dataset: LensDataset
    x_axis: str
    breakdown: str
    value: str
    legend_show: bool = True
    legend_position: str = 'right'

    def to_ts(self) -> str:
        """Convert to TypeScript LensHeatmapConfig."""
        lines = [
            "chartType: 'heatmap'",
            f'title: {json.dumps(self.title)}',
            f'dataset: {self.dataset.to_ts()}',
            f'xAxis: {json.dumps(self.x_axis)}',
            f'breakdown: {json.dumps(self.breakdown)}',
            f'value: {json.dumps(self.value)}',
            f'legend: {{ show: {"true" if self.legend_show else "false"}, position: {json.dumps(self.legend_position)} }}',
        ]
        return '{\n    ' + ',\n    '.join(lines) + '\n  }'


# Union type for all config types
LensConfig = LensMetricConfig | LensPieConfig | LensXYConfig | LensGaugeConfig | LensHeatmapConfig


def generate_fixture_script(
    config: LensConfig,
    output_name: str,
    time_range: TimeRange | None = None,
) -> str:
    """Generate TypeScript script content for fixture generation.

    Args:
        config: The Lens configuration to generate.
        output_name: Name for the output file (without .json extension).
        time_range: Optional time range for the fixture.

    Returns:
        TypeScript script content as a string.
    """
    if time_range is None:
        time_range = TimeRange()

    time_range_ts = json.dumps(time_range.to_dict())

    # Determine the correct type import based on config type
    type_map = {
        LensMetricConfig: 'LensMetricConfig',
        LensPieConfig: 'LensPieConfig',
        LensXYConfig: 'LensXYConfig',
        LensGaugeConfig: 'LensGaugeConfig',
        LensHeatmapConfig: 'LensHeatmapConfig',
    }
    type_name = type_map[type(config)]

    return f"""#!/usr/bin/env node
import type {{ {type_name} }} from '@kbn/lens-embeddable-utils/config_builder';
import {{ generateFixture }} from '../generator-utils.js';

const config: {type_name} = {config.to_ts()};

await generateFixture(
  '{output_name}.json',
  config,
  {{ timeRange: {time_range_ts} }},
  import.meta.url
);
"""


class FixtureGenerator:
    """Generate Kibana fixtures by invoking LensConfigBuilder via Docker.

    This class provides a Python API for generating Kibana Lens fixtures
    using the same LensConfigBuilder API that Kibana uses internally.
    """

    def __init__(
        self,
        kibana_version: str = DEFAULT_KIBANA_VERSION,
        auto_pull: bool = True,
    ) -> None:
        """Initialize the fixture generator.

        Args:
            kibana_version: Kibana version to use for fixture generation.
            auto_pull: Whether to automatically pull the Docker image if not available.
        """
        self.kibana_version = kibana_version
        self.base_image = f'{DEFAULT_BASE_IMAGE}:{kibana_version}'
        self._temp_dirs: list[Path] = []

        if not docker_available():
            msg = 'Docker is not available'
            raise RuntimeError(msg)

        if not fixture_image_available(kibana_version):
            if auto_pull:
                if not pull_fixture_image(kibana_version):
                    msg = f'Failed to pull fixture image: {self.base_image}'
                    raise RuntimeError(msg)
            else:
                msg = f'Fixture image not available: {self.base_image}'
                raise RuntimeError(msg)

    def generate(
        self,
        config: LensConfig,
        output_name: str,
        time_range: TimeRange | None = None,
    ) -> dict[str, Any]:
        """Generate a fixture from a configuration.

        Args:
            config: The Lens configuration.
            output_name: Name for the output file (without .json extension).
            time_range: Optional time range configuration.

        Returns:
            The generated fixture as a dictionary.
        """
        # Create temporary directories for script and output
        temp_dir = Path(tempfile.mkdtemp(prefix='fixture_gen_'))
        self._temp_dirs.append(temp_dir)
        examples_dir = temp_dir / 'examples'
        output_dir = temp_dir / 'output'
        examples_dir.mkdir()
        output_dir.mkdir()

        # Generate the TypeScript script
        script_content = generate_fixture_script(config, output_name, time_range)
        script_path = examples_dir / 'generated.ts'
        script_path.write_text(script_content)

        # Run the fixture generator
        cmd = [
            'docker',
            'run',
            '--rm',
            '-v',
            f'{output_dir}:/kibana/output',
            '-v',
            f'{examples_dir}:/kibana/examples:ro',
            '-v',
            f'{_FIXTURE_GEN_DIR}/generator-utils.ts:/kibana/generator-utils.ts:ro',
            '-v',
            f'{_FIXTURE_GEN_DIR}/dataviews-mock.js:/kibana/dataviews-mock.js:ro',
            '-e',
            'NODE_OPTIONS=--max-old-space-size=8192',
            '-e',
            f'KIBANA_VERSION={self.kibana_version}',
            self.base_image,
            'tsx',
            'examples/generated.ts',
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes
            check=False,
        )

        if result.returncode != 0:
            msg = f'Fixture generation failed: {result.stderr}'
            raise RuntimeError(msg)

        # Load and return the generated fixture
        fixture_path = output_dir / self.kibana_version / f'{output_name}.json'
        if not fixture_path.exists():
            msg = f'Generated fixture not found: {fixture_path}'
            raise RuntimeError(msg)

        return json.loads(fixture_path.read_text())

    def generate_from_existing_example(self, example_name: str) -> dict[str, dict[str, Any]]:
        """Generate fixtures using an existing example script.

        Args:
            example_name: Name of the example script (e.g., 'metric-basic.ts').

        Returns:
            Dictionary mapping fixture names to their content.
        """
        # Create temporary output directory
        temp_dir = Path(tempfile.mkdtemp(prefix='fixture_gen_'))
        self._temp_dirs.append(temp_dir)
        output_dir = temp_dir / 'output'
        output_dir.mkdir()

        # Run the fixture generator
        cmd = [
            'docker',
            'run',
            '--rm',
            '-v',
            f'{output_dir}:/kibana/output',
            '-v',
            f'{_FIXTURE_GEN_DIR}/examples:/kibana/examples:ro',
            '-v',
            f'{_FIXTURE_GEN_DIR}/generator-utils.ts:/kibana/generator-utils.ts:ro',
            '-v',
            f'{_FIXTURE_GEN_DIR}/dataviews-mock.js:/kibana/dataviews-mock.js:ro',
            '-e',
            'NODE_OPTIONS=--max-old-space-size=8192',
            '-e',
            f'KIBANA_VERSION={self.kibana_version}',
            self.base_image,
            'tsx',
            f'examples/{example_name}',
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )

        if result.returncode != 0:
            msg = f'Fixture generation failed: {result.stderr}'
            raise RuntimeError(msg)

        # Load all generated fixtures
        fixtures: dict[str, dict[str, Any]] = {}
        fixture_dir = output_dir / self.kibana_version
        if fixture_dir.exists():
            for fixture_file in fixture_dir.glob('*.json'):
                fixtures[fixture_file.stem] = json.loads(fixture_file.read_text())

        return fixtures

    def cleanup(self) -> None:
        """Clean up temporary directories."""
        for temp_dir in self._temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        self._temp_dirs.clear()

    def __del__(self) -> None:
        """Ensure cleanup on destruction."""
        self.cleanup()
