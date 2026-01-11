"""Fixture generator integration for pytest.

This module provides utilities to invoke the TypeScript fixture generator
directly from pytest using Docker and the aiodocker library.
"""

from __future__ import annotations

import contextlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiodocker

if TYPE_CHECKING:
    from collections.abc import Mapping

# Project paths
_TESTS_DIR = Path(__file__).parent.parent
_COMPILER_DIR = _TESTS_DIR.parent
_PROJECT_ROOT = _COMPILER_DIR.parent
_FIXTURE_GEN_DIR = _PROJECT_ROOT / 'fixture-generator'

# Docker image configuration
DEFAULT_KIBANA_VERSION = 'v9.2.0'
DEFAULT_BASE_IMAGE = 'ghcr.io/strawgate/kb-yaml-to-lens/kibana-base'


async def docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        docker = aiodocker.Docker()
        await docker.close()
    except Exception:
        return False
    return True


async def fixture_image_available(kibana_version: str = DEFAULT_KIBANA_VERSION) -> bool:
    """Check if the fixture generator Docker image is available locally."""
    image_name = f'{DEFAULT_BASE_IMAGE}:{kibana_version}'
    try:
        docker = aiodocker.Docker()
        try:
            await docker.images.inspect(image_name)
        except aiodocker.DockerError:
            return False
        else:
            return True
        finally:
            await docker.close()
    except Exception:
        return False


async def pull_fixture_image(kibana_version: str = DEFAULT_KIBANA_VERSION) -> bool:
    """Pull the fixture generator Docker image from GHCR."""
    image_name = f'{DEFAULT_BASE_IMAGE}:{kibana_version}'
    try:
        docker = aiodocker.Docker()
        try:
            await docker.images.pull(image_name)
        except aiodocker.DockerError:
            return False
        else:
            return True
        finally:
            await docker.close()
    except Exception:
        return False


class FixtureGenerator:
    """Generate Kibana fixtures by invoking LensConfigBuilder via Docker.

    This class provides a Python API for generating Kibana Lens fixtures
    using the same LensConfigBuilder API that Kibana uses internally.

    Usage:
        async with FixtureGenerator() as generator:
            fixture = await generator.generate(typescript_config, 'metric-basic')

    Or manually:
        generator = await FixtureGenerator.create()
        try:
            fixture = await generator.generate(typescript_config, 'metric-basic')
        finally:
            await generator.cleanup()
    """

    def __init__(
        self,
        kibana_version: str = DEFAULT_KIBANA_VERSION,
    ) -> None:
        """Initialize the fixture generator.

        Args:
            kibana_version: Kibana version to use for fixture generation.

        Note:
            Use FixtureGenerator.create() or async context manager for proper initialization.
        """
        self.kibana_version = kibana_version
        self.base_image = f'{DEFAULT_BASE_IMAGE}:{kibana_version}'
        self._temp_dirs: list[Path] = []
        self._docker: aiodocker.Docker | None = None
        self._initialized = False

    @classmethod
    async def create(
        cls,
        kibana_version: str = DEFAULT_KIBANA_VERSION,
        auto_pull: bool = True,
    ) -> FixtureGenerator:
        """Create and initialize a fixture generator.

        Args:
            kibana_version: Kibana version to use for fixture generation.
            auto_pull: Whether to automatically pull the Docker image if not available.

        Returns:
            An initialized FixtureGenerator instance.

        Raises:
            RuntimeError: If Docker is not available or image pull fails.
        """
        generator = cls(kibana_version)
        await generator._initialize(auto_pull)
        return generator

    async def _initialize(self, auto_pull: bool = True) -> None:
        """Initialize the Docker connection and ensure image is available."""
        if self._initialized:
            return

        try:
            self._docker = aiodocker.Docker()
        except Exception as e:
            msg = 'Docker is not available'
            raise RuntimeError(msg) from e

        # Check if image is available
        try:
            await self._docker.images.inspect(self.base_image)
        except aiodocker.DockerError as inspect_err:
            if auto_pull:
                try:
                    await self._docker.images.pull(self.base_image)
                except aiodocker.DockerError as e:
                    msg = f'Failed to pull fixture image: {self.base_image}'
                    raise RuntimeError(msg) from e
            else:
                msg = f'Fixture image not available: {self.base_image}'
                raise RuntimeError(msg) from inspect_err

        self._initialized = True

    async def __aenter__(self) -> FixtureGenerator:
        """Enter async context manager."""
        await self._initialize()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        """Exit async context manager, ensuring cleanup."""
        await self.cleanup()

    async def generate(
        self,
        typescript_config: str,
        output_name: str,
        time_range: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        """Generate a fixture from a TypeScript configuration.

        Args:
            typescript_config: Raw TypeScript LensConfigBuilder configuration object.
                This should be a valid TypeScript object literal that matches
                one of the LensConfigBuilder config types (LensMetricConfig,
                LensPieConfig, etc.).
            output_name: Name for the output file (without .json extension).
            time_range: Optional time range dict with 'from', 'to', 'type' keys.
                Defaults to {'from': 'now-24h', 'to': 'now', 'type': 'relative'}.

        Returns:
            The generated fixture as a dictionary.

        Example:
            typescript_config = '''
            {
                chartType: 'metric',
                title: 'Basic Count Metric',
                dataset: { esql: 'FROM logs-* | STATS count = COUNT()' },
                value: 'count',
            }
            '''
            fixture = await generator.generate(typescript_config, 'metric-basic')
        """
        if not self._initialized or self._docker is None:
            msg = 'FixtureGenerator not initialized. Use create() or async context manager.'
            raise RuntimeError(msg)

        if time_range is None:
            time_range = {'from': 'now-24h', 'to': 'now', 'type': 'relative'}

        # Create temporary directories for script and output
        temp_dir = Path(tempfile.mkdtemp(prefix='fixture_gen_'))
        self._temp_dirs.append(temp_dir)
        examples_dir = temp_dir / 'examples'
        output_dir = temp_dir / 'output'
        examples_dir.mkdir()
        output_dir.mkdir()

        # Generate the TypeScript script
        script_content = self._generate_script(typescript_config, output_name, time_range)
        script_path = examples_dir / 'generated.ts'
        script_path.write_text(script_content)

        # Create and run the container
        config = {
            'Image': self.base_image,
            'Cmd': ['tsx', 'examples/generated.ts'],
            'Env': [
                'NODE_OPTIONS=--max-old-space-size=8192',
                f'KIBANA_VERSION={self.kibana_version}',
            ],
            'HostConfig': {
                'Binds': [
                    f'{output_dir}:/kibana/output',
                    f'{examples_dir}:/kibana/examples:ro',
                    f'{_FIXTURE_GEN_DIR}/generator-utils.ts:/kibana/generator-utils.ts:ro',
                    f'{_FIXTURE_GEN_DIR}/dataviews-mock.js:/kibana/dataviews-mock.js:ro',
                ],
                'AutoRemove': True,
            },
        }

        container = await self._docker.containers.create(config=config)
        try:
            await container.start()
            await container.wait()

            # Check logs for errors
            logs = await container.log(stdout=True, stderr=True)
            log_output = ''.join(logs)
            if 'error' in log_output.lower() and 'TypeError' in log_output:
                msg = f'Fixture generation failed: {log_output}'
                raise RuntimeError(msg)
        finally:
            # Container auto-removes, but ensure cleanup
            with contextlib.suppress(aiodocker.DockerError):
                await container.delete(force=True)

        # Load and return the generated fixture
        fixture_path = output_dir / self.kibana_version / f'{output_name}.json'
        if not fixture_path.exists():
            msg = f'Generated fixture not found: {fixture_path}'
            raise RuntimeError(msg)

        return json.loads(fixture_path.read_text())

    def _generate_script(
        self,
        typescript_config: str,
        output_name: str,
        time_range: Mapping[str, str],
    ) -> str:
        """Generate TypeScript script content for fixture generation."""
        time_range_json = json.dumps(dict(time_range))

        # Determine the config type from the TypeScript - look for chartType
        # We need to import the right type
        config_lower = typescript_config.lower()
        if "'metric'" in config_lower or '"metric"' in config_lower:
            type_name = 'LensMetricConfig'
        elif "'pie'" in config_lower or '"pie"' in config_lower:
            type_name = 'LensPieConfig'
        elif "'xy'" in config_lower or '"xy"' in config_lower:
            type_name = 'LensXYConfig'
        elif "'gauge'" in config_lower or '"gauge"' in config_lower:
            type_name = 'LensGaugeConfig'
        elif "'heatmap'" in config_lower or '"heatmap"' in config_lower:
            type_name = 'LensHeatmapConfig'
        elif "'tagcloud'" in config_lower or '"tagcloud"' in config_lower:
            type_name = 'LensTagcloudConfig'
        elif "'treemap'" in config_lower or '"treemap"' in config_lower:
            type_name = 'LensTreemapConfig'
        elif "'waffle'" in config_lower or '"waffle"' in config_lower:
            type_name = 'LensWaffleConfig'
        elif "'datatable'" in config_lower or '"datatable"' in config_lower:
            type_name = 'LensDatatableConfig'
        else:
            # Fallback - let TypeScript figure it out
            type_name = 'LensConfig'

        return f"""#!/usr/bin/env node
import type {{ {type_name} }} from '@kbn/lens-embeddable-utils/config_builder';
import {{ generateFixture }} from '../generator-utils.js';

const config: {type_name} = {typescript_config};

await generateFixture(
  '{output_name}.json',
  config,
  {{ timeRange: {time_range_json} }},
  import.meta.url
);
"""

    async def cleanup(self) -> None:
        """Clean up temporary directories and close Docker connection."""
        for temp_dir in self._temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        self._temp_dirs.clear()

        if self._docker is not None:
            await self._docker.close()
            self._docker = None
            self._initialized = False
