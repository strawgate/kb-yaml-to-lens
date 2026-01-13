"""Fixture generator integration for pytest.

Simple Docker-based fixture generation using aiodocker.
Each function does one thing and does it well.
"""

import asyncio
import base64
import json
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import aiodocker

# Project paths
_TESTS_DIR = Path(__file__).parent.parent
_COMPILER_DIR = _TESTS_DIR.parent
_PROJECT_ROOT = _COMPILER_DIR.parent
_FIXTURE_GEN_DIR = _PROJECT_ROOT / 'fixture-generator'

# Docker configuration
DEFAULT_KIBANA_VERSION = 'v9.2.2'
DEFAULT_BASE_IMAGE = 'ghcr.io/strawgate/kb-yaml-to-lens/kibana-base'


# =============================================================================
# Docker client helpers
# =============================================================================


@asynccontextmanager
async def docker_client() -> AsyncIterator[aiodocker.Docker]:
    """Context manager for Docker client with automatic cleanup."""
    docker = aiodocker.Docker()
    try:
        yield docker
    finally:
        await docker.close()


async def docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        async with docker_client() as docker:
            await docker.version()
        return True
    except Exception:
        return False


async def ensure_image(docker: aiodocker.Docker, image: str) -> None:
    """Ensure a Docker image is available, pulling if necessary.

    Args:
        docker: Docker client
        image: Image name (e.g. 'repo/image:tag')

    Raises:
        RuntimeError: If image cannot be obtained
    """
    try:
        await docker.images.inspect(image)
    except aiodocker.DockerError:
        # Image not available, try to pull
        try:
            await docker.images.pull(image)
        except aiodocker.DockerError as e:
            msg = f'Failed to pull image {image}'
            raise RuntimeError(msg) from e


# =============================================================================
# Container operations
# =============================================================================


@asynccontextmanager
async def managed_container(
    docker: aiodocker.Docker,
    config: dict[str, Any],
) -> AsyncIterator[Any]:
    """Context manager for a Docker container with automatic cleanup.

    Args:
        docker: Docker client
        config: Container configuration dict

    Yields:
        Container object
    """
    container = await docker.containers.create(config=config)
    try:
        await container.start()  # pyright: ignore[reportUnknownMemberType]
        yield container
    finally:
        await container.delete(force=True)


async def exec_command(container: Any, command: str, timeout: float = 30.0) -> tuple[int, str]:
    """Execute a command in a container and return exit code and output.

    Args:
        container: Docker container object
        command: Shell command to execute
        timeout: Timeout in seconds

    Returns:
        Tuple of (exit_code, output_text)
    """
    exec_instance = await container.exec(cmd=['bash', '-c', command])  # pyright: ignore[reportUnknownMemberType]
    stream = exec_instance.start(detach=False)  # pyright: ignore[reportUnknownMemberType]

    # Read all output from stream
    output_chunks = []
    while True:
        try:
            chunk = await asyncio.wait_for(stream.read_out(), timeout=timeout)  # pyright: ignore[reportUnknownMemberType]
            if chunk is None:
                break
            # Handle aiodocker Message objects
            if hasattr(chunk, 'data'):
                data = chunk.data  # pyright: ignore[reportUnknownMemberType,reportUnknownVariableType]
                output_chunks.append(data.decode() if isinstance(data, bytes) else str(data))
            elif isinstance(chunk, bytes):
                output_chunks.append(chunk.decode())
            else:
                output_chunks.append(str(chunk))
        except TimeoutError:
            break
        except Exception:
            break

    # Get exit code
    result = await exec_instance.inspect()  # pyright: ignore[reportUnknownMemberType]
    exit_code = result.get('ExitCode', -1)

    return exit_code, ''.join(output_chunks)


# =============================================================================
# Fixture generation helpers
# =============================================================================


def build_typescript_script(
    typescript_config: str,
    output_name: str,
    type_name: str,
    time_range: Mapping[str, str] | None = None,
) -> str:
    """Build a TypeScript script for fixture generation.

    Args:
        typescript_config: Raw TypeScript config object
        output_name: Output filename (without .json)
        type_name: TypeScript type name
        time_range: Optional time range dict

    Returns:
        Complete TypeScript script as string
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


async def run_script_in_container(container: Any, script_content: str) -> None:
    """Run a TypeScript script in a container.

    Args:
        container: Docker container (must have tsx, node, etc.)
        script_content: TypeScript script to execute

    Raises:
        RuntimeError: If script execution fails
    """
    # Step 1: Create directories
    exit_code, output = await exec_command(container, 'mkdir -p /tmp /kibana/examples')
    if exit_code != 0:
        msg = f'Failed to create directories: {output}'
        raise RuntimeError(msg)

    # Step 2: Write script file
    script_b64 = base64.b64encode(script_content.encode()).decode()
    exit_code, output = await exec_command(container, f'echo {script_b64} | base64 -d > /kibana/examples/gen.ts')
    if exit_code != 0:
        msg = f'Failed to write script: {output}'
        raise RuntimeError(msg)

    # Step 3: Execute script
    exit_code, output = await exec_command(container, 'tsx /kibana/examples/gen.ts')
    if exit_code != 0:
        msg = f'Fixture generation failed:\n{output}'
        raise RuntimeError(msg)


def build_container_config(
    image: str,
    output_dir: Path,
    kibana_version: str,
) -> dict[str, Any]:
    """Build Docker container configuration for persistent fixture generation.

    Args:
        image: Docker image name
        output_dir: Host directory to mount for output
        kibana_version: Kibana version

    Returns:
        Container config dict
    """
    return {
        'Image': image,
        'Cmd': ['tail', '-f', '/dev/null'],  # Keep alive
        'Env': [
            'NODE_OPTIONS=--max-old-space-size=8192',
            f'KIBANA_VERSION={kibana_version}',
        ],
        'HostConfig': {
            'Binds': [
                f'{output_dir}:/kibana/output',
                f'{_FIXTURE_GEN_DIR}/generator-utils.ts:/kibana/examples/generator-utils.ts:ro',
                f'{_FIXTURE_GEN_DIR}/dataviews-mock.js:/kibana/examples/dataviews-mock.js:ro',
            ],
        },
    }


# =============================================================================
# High-level fixture generation
# =============================================================================


@asynccontextmanager
async def shared_fixture_container(
    output_dir: Path,
    kibana_version: str = DEFAULT_KIBANA_VERSION,
) -> AsyncIterator[Any]:
    """Create a persistent container for multiple fixture generations.

    Args:
        output_dir: Directory for fixture output
        kibana_version: Kibana version

    Yields:
        Container object that can be reused

    Raises:
        RuntimeError: If Docker or image unavailable
    """
    image = f'{DEFAULT_BASE_IMAGE}:{kibana_version}'

    async with docker_client() as docker:
        await ensure_image(docker, image)
        config = build_container_config(image, output_dir, kibana_version)
        async with managed_container(docker, config) as container:
            yield container


async def generate_fixture(
    container: Any,
    output_dir: Path,
    typescript_config: str,
    output_name: str,
    type_name: str,
    time_range: Mapping[str, str] | None = None,
    kibana_version: str = DEFAULT_KIBANA_VERSION,
) -> dict[str, Any]:
    """Generate a fixture from TypeScript configuration.

    Args:
        container: Docker container to run script in
        output_dir: Output directory where fixture will be written
        typescript_config: Raw TypeScript config object
        output_name: Output filename (without .json)
        type_name: TypeScript type name
        time_range: Optional time range
        kibana_version: Kibana version

    Returns:
        Generated fixture as dict

    Raises:
        RuntimeError: If generation fails
    """
    script = build_typescript_script(typescript_config, output_name, type_name, time_range)
    await run_script_in_container(container, script)

    # Read generated fixture
    fixture_path = output_dir / kibana_version / f'{output_name}.json'
    if not fixture_path.exists():
        msg = f'Generated fixture not found: {fixture_path}'
        raise RuntimeError(msg)

    return json.loads(fixture_path.read_text())
