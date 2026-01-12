"""Fixture generator integration for pytest.

This module provides utilities to invoke the TypeScript fixture generator
directly from pytest using Docker and the aiodocker library.

The main entry point is the `fixture_container` async context manager which
handles container lifecycle. Tests can use it directly:

    async with fixture_container(output_dir) as container:
        script = generate_fixture_script(ts_config, 'output', 'LensMetricConfig')
        await run_fixture_script(container, script)
        # Read output from output_dir

For simpler usage, the `generate_fixture` function wraps all of this:

    fixture = await generate_fixture(ts_config, 'output', 'LensMetricConfig')
"""

from __future__ import annotations

import base64
import json
import re
import shutil
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiodocker

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping

# Project paths
_TESTS_DIR = Path(__file__).parent.parent
_COMPILER_DIR = _TESTS_DIR.parent
_PROJECT_ROOT = _COMPILER_DIR.parent
_FIXTURE_GEN_DIR = _PROJECT_ROOT / 'fixture-generator'

# Docker image configuration
DEFAULT_KIBANA_VERSION = 'v9.2.2'
DEFAULT_BASE_IMAGE = 'ghcr.io/strawgate/kb-yaml-to-lens/kibana-base'

# Error patterns to detect in container output
_ERROR_PATTERN = re.compile(r'\b[A-Z][a-zA-Z]*Error\b')


async def docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        docker = aiodocker.Docker()
        try:
            await docker.version()
        finally:
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


def generate_fixture_script(
    typescript_config: str,
    output_name: str,
    type_name: str,
    time_range: Mapping[str, str] | None = None,
) -> str:
    """Generate TypeScript script content for fixture generation.

    Args:
        typescript_config: Raw TypeScript LensConfigBuilder configuration object.
        output_name: Name for the output file (without .json extension).
        type_name: TypeScript type name for the config (e.g., 'LensMetricConfig').
        time_range: Optional time range dict with 'from', 'to', 'type' keys.

    Returns:
        TypeScript script content ready to execute in the fixture container.
    """
    if time_range is None:
        time_range = {'from': 'now-24h', 'to': 'now', 'type': 'relative'}

    time_range_json = json.dumps(dict(time_range))

    return f"""#!/usr/bin/env node
import type {{ {type_name} }} from '@kbn/lens-embeddable-utils/config_builder';
import {{ generateFixture }} from './generator-utils.js';

const config: {type_name} = {typescript_config};

(async () => {{
  await generateFixture(
    '{output_name}.json',
    config,
    {{ timeRange: {time_range_json} }},
    import.meta.url
  );
}})().catch((err) => {{
  console.error(err);
  process.exit(1);
}});
"""


class FixtureContainer:
    """Wrapper around a Docker container for fixture generation.

    This class manages the container lifecycle and provides methods
    for running fixture scripts. It's designed to be used with the
    `fixture_container` async context manager.
    """

    def __init__(
        self,
        docker: aiodocker.Docker,
        output_dir: Path,
        kibana_version: str,
    ) -> None:
        """Initialize the fixture container wrapper.

        Args:
            docker: The aiodocker client.
            output_dir: Local directory to mount for output.
            kibana_version: Kibana version for the base image.
        """
        self.docker = docker
        self.output_dir = output_dir
        self.kibana_version = kibana_version
        self.base_image = f'{DEFAULT_BASE_IMAGE}:{kibana_version}'

    async def run_script(self, script_content: str) -> None:
        """Run a TypeScript fixture generation script in the container.

        Args:
            script_content: TypeScript script content to execute.

        Raises:
            RuntimeError: If the script execution fails.
        """
        script_b64 = base64.b64encode(script_content.encode()).decode()
        bash_cmd = f'echo {script_b64} | base64 -d > /kibana/gen.ts && tsx /kibana/gen.ts'

        config = {
            'Image': self.base_image,
            'Cmd': ['bash', '-c', bash_cmd],
            'Env': [
                'NODE_OPTIONS=--max-old-space-size=8192',
                f'KIBANA_VERSION={self.kibana_version}',
            ],
            'HostConfig': {
                'Binds': [
                    f'{self.output_dir}:/kibana/output',
                    f'{_FIXTURE_GEN_DIR}/generator-utils.ts:/kibana/generator-utils.ts:ro',
                    f'{_FIXTURE_GEN_DIR}/dataviews-mock.js:/kibana/dataviews-mock.js:ro',
                ],
            },
        }

        container = await self.docker.containers.create(config=config)
        try:
            await container.start()  # pyright: ignore[reportUnknownMemberType]
            await container.wait()  # pyright: ignore[reportUnknownMemberType]

            logs = await container.log(stdout=True, stderr=True)  # pyright: ignore[reportUnknownMemberType]
            log_output = ''.join(logs)
            if _ERROR_PATTERN.search(log_output):
                msg = f'Fixture generation failed: {log_output}'
                raise RuntimeError(msg)
        finally:
            await container.delete(force=True)


@asynccontextmanager
async def fixture_container(
    output_dir: Path,
    kibana_version: str = DEFAULT_KIBANA_VERSION,
    auto_pull: bool = True,
) -> AsyncIterator[FixtureContainer]:
    """Async context manager for fixture generation with Docker.

    This is the primary interface for running fixture generation. It handles:
    - Docker client lifecycle
    - Image availability checks (with optional auto-pull)
    - Cleanup on exit

    Example:
        output_dir = Path(tempfile.mkdtemp())
        async with fixture_container(output_dir) as container:
            script = generate_fixture_script(ts_config, 'metric', 'LensMetricConfig')
            await container.run_script(script)
            # Read results from output_dir / kibana_version / 'metric.json'

    Args:
        output_dir: Directory where fixture output will be written.
        kibana_version: Kibana version to use for fixture generation.
        auto_pull: Whether to automatically pull the image if not available.

    Yields:
        FixtureContainer instance for running scripts.

    Raises:
        RuntimeError: If Docker is not available or image cannot be obtained.
    """
    base_image = f'{DEFAULT_BASE_IMAGE}:{kibana_version}'

    try:
        docker = aiodocker.Docker()
    except Exception as e:
        msg = 'Docker is not available'
        raise RuntimeError(msg) from e

    try:
        # Ensure image is available
        try:
            await docker.images.inspect(base_image)
        except aiodocker.DockerError as inspect_err:
            if auto_pull:
                try:
                    await docker.images.pull(base_image)
                except aiodocker.DockerError as e:
                    msg = f'Failed to pull fixture image: {base_image}'
                    raise RuntimeError(msg) from e
            else:
                msg = f'Fixture image not available: {base_image}'
                raise RuntimeError(msg) from inspect_err

        yield FixtureContainer(docker, output_dir, kibana_version)
    finally:
        await docker.close()


async def generate_fixture(  # noqa: PLR0913
    typescript_config: str,
    output_name: str,
    type_name: str,
    time_range: Mapping[str, str] | None = None,
    kibana_version: str = DEFAULT_KIBANA_VERSION,
    auto_pull: bool = True,
) -> dict[str, Any]:
    """Generate a fixture from a TypeScript configuration.

    This is a convenience function that wraps the fixture_container context
    manager for simple, one-off fixture generation. For multiple fixtures
    or more control, use fixture_container directly.

    Args:
        typescript_config: Raw TypeScript LensConfigBuilder configuration object.
        output_name: Name for the output file (without .json extension).
        type_name: TypeScript type name for the config (e.g., 'LensMetricConfig').
        time_range: Optional time range dict with 'from', 'to', 'type' keys.
        kibana_version: Kibana version to use for fixture generation.
        auto_pull: Whether to automatically pull the Docker image if not available.

    Returns:
        The generated fixture as a dictionary.

    Raises:
        RuntimeError: If Docker is not available, image pull fails, or generation fails.
    """
    output_dir = Path(tempfile.mkdtemp(prefix='fixture_gen_output_'))
    try:
        async with fixture_container(output_dir, kibana_version, auto_pull) as container:
            script = generate_fixture_script(typescript_config, output_name, type_name, time_range)
            await container.run_script(script)

            fixture_path = output_dir / kibana_version / f'{output_name}.json'
            if not fixture_path.exists():
                msg = f'Generated fixture not found: {fixture_path}'
                raise RuntimeError(msg)

            return json.loads(fixture_path.read_text())
    finally:
        if output_dir.exists():
            shutil.rmtree(output_dir)
