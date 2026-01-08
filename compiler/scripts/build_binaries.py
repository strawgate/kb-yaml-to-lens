#!/usr/bin/env python3
"""Build standalone binaries for kb-dashboard using PyInstaller."""

import platform
import shutil
import subprocess
from pathlib import Path

COMPILER_ROOT = Path(__file__).parent.parent
PROJECT_ROOT = COMPILER_ROOT.parent


def get_platform_name() -> str:
    """Get platform name for binary naming (e.g., 'linux-x64', 'darwin-arm64')."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch = 'x64' if machine in ('x86_64', 'amd64') else 'arm64' if machine in ('aarch64', 'arm64') else machine
    return f'{system}-{arch}'


def main() -> None:
    """Build standalone binary for current platform."""
    platform_name = get_platform_name()
    binary_name = f'kb-dashboard-{platform_name}'
    if platform.system() == 'Windows':
        binary_name += '.exe'

    print(f'Building {binary_name}...')

    # Clean previous builds
    for d in ['build', 'dist']:
        path = COMPILER_ROOT / d
        if path.exists() is True:
            shutil.rmtree(path)

    # Build with PyInstaller
    cli_path = COMPILER_ROOT / 'src' / 'dashboard_compiler' / 'cli.py'
    subprocess.run(  # noqa: S603
        ['pyinstaller', '--name', binary_name, '--onefile', '--clean', '--noconfirm', str(cli_path)],  # noqa: S607
        check=True,
        cwd=COMPILER_ROOT,
    )

    # Report success
    binary_path = COMPILER_ROOT / 'dist' / binary_name
    size_mb = binary_path.stat().st_size / (1024 * 1024)
    print(f'Built: {binary_path} ({size_mb:.1f} MB)')


if __name__ == '__main__':
    main()
