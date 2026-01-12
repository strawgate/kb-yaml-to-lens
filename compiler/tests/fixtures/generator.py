"""Fixture generator integration for pytest.

This module provides utilities to invoke the TypeScript fixture generator
directly from pytest using Docker and the aiodocker library.
"""

from __future__ import annotations

import base64
import json
import re
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


def _generate_script(
    typescript_config: str,
    output_name: str,
    type_name: str,
    time_range: Mapping[str, str],
) -> str:
    """Generate TypeScript script content for fixture generation."""
    time_range_json = json.dumps(dict(time_range))

    return f"""#!/usr/bin/env node
import type {{ {type_name} }} from '@kbn/lens-embeddable-utils/config_builder';
import {{ generateFixture }} from './generator-utils.js';

const config: {type_name} = {typescript_config};

await generateFixture(
  '{output_name}.json',
  config,
  {{ timeRange: {time_range_json} }},
  import.meta.url
);
"""


async def _ensure_image_available(docker: aiodocker.Docker, base_image: str, auto_pull: bool) -> None:
    """Ensure the Docker image is available, pulling if necessary."""
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


async def _run_fixture_container(
    docker: aiodocker.Docker,
    base_image: str,
    script_b64: str,
    output_dir: Path,
    kibana_version: str,
) -> None:
    """Run the fixture generation container."""
    bash_cmd = f'echo {script_b64} | base64 -d > /kibana/gen.ts && tsx /kibana/gen.ts'

    config = {
        'Image': base_image,
        'Cmd': ['bash', '-c', bash_cmd],
        'Env': [
            'NODE_OPTIONS=--max-old-space-size=8192',
            f'KIBANA_VERSION={kibana_version}',
        ],
        'HostConfig': {
            'Binds': [
                f'{output_dir}:/kibana/output',
                f'{_FIXTURE_GEN_DIR}/generator-utils.ts:/kibana/generator-utils.ts:ro',
                f'{_FIXTURE_GEN_DIR}/dataviews-mock.js:/kibana/dataviews-mock.js:ro',
            ],
        },
    }

    container = await docker.containers.create(config=config)
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


async def generate_fixture(  # noqa: PLR0913
    typescript_config: str,
    output_name: str,
    type_name: str,
    time_range: Mapping[str, str] | None = None,
    kibana_version: str = DEFAULT_KIBANA_VERSION,
    auto_pull: bool = True,
) -> dict[str, Any]:
    """Generate a fixture from a TypeScript configuration.

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
    if time_range is None:
        time_range = {'from': 'now-24h', 'to': 'now', 'type': 'relative'}

    base_image = f'{DEFAULT_BASE_IMAGE}:{kibana_version}'

    try:
        docker = aiodocker.Docker()
    except Exception as e:
        msg = 'Docker is not available'
        raise RuntimeError(msg) from e

    try:
        await _ensure_image_available(docker, base_image, auto_pull)

        output_dir = Path(tempfile.mkdtemp(prefix='fixture_gen_output_'))
        try:
            script_content = _generate_script(typescript_config, output_name, type_name, time_range)
            script_b64 = base64.b64encode(script_content.encode()).decode()

            await _run_fixture_container(docker, base_image, script_b64, output_dir, kibana_version)

            fixture_path = output_dir / kibana_version / f'{output_name}.json'
            if not fixture_path.exists():
                msg = f'Generated fixture not found: {fixture_path}'
                raise RuntimeError(msg)

            return json.loads(fixture_path.read_text())
        finally:
            if output_dir.exists():
                shutil.rmtree(output_dir)
    finally:
        await docker.close()
