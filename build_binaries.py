#!/usr/bin/env python3
"""Build standalone binaries for kb-dashboard using PyInstaller.

This script creates platform-specific executable binaries that bundle
the Python interpreter and all dependencies into a single file.

Usage:
    python build_binaries.py

Requirements:
    - PyInstaller must be installed: pip install pyinstaller
"""

import platform
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / 'dist'
BUILD_DIR = PROJECT_ROOT / 'build'


def get_platform_name() -> str:
    """Get normalized platform name for binary naming.

    Returns:
        Platform identifier string (e.g., 'linux-x64', 'darwin-arm64', 'windows-x64').

    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    if machine in ('x86_64', 'amd64'):
        arch = 'x64'
    elif machine in ('aarch64', 'arm64'):
        arch = 'arm64'
    else:
        arch = machine

    return f'{system}-{arch}'


def clean_build_artifacts() -> None:
    """Remove previous build artifacts."""
    if BUILD_DIR.exists():
        print(f'Cleaning build directory: {BUILD_DIR}')
        shutil.rmtree(BUILD_DIR)

    if DIST_DIR.exists():
        print(f'Cleaning dist directory: {DIST_DIR}')
        shutil.rmtree(DIST_DIR)


def build_binary() -> None:
    """Build standalone binary using PyInstaller."""
    platform_name = get_platform_name()
    binary_name = f'kb-dashboard-{platform_name}'

    if platform.system() == 'Windows':
        binary_name += '.exe'

    print(f'Building binary for platform: {platform_name}')
    print(f'Output binary name: {binary_name}')

    cli_path = PROJECT_ROOT / 'src' / 'dashboard_compiler' / 'cli.py'

    if not cli_path.exists():
        print(f'Error: CLI entry point not found at {cli_path}')
        sys.exit(1)

    pyinstaller_args = [
        'pyinstaller',
        '--name',
        binary_name,
        '--onefile',
        '--clean',
        '--noconfirm',
        str(cli_path),
    ]

    print(f'Running: {" ".join(pyinstaller_args)}')

    try:
        subprocess.run(pyinstaller_args, check=True, cwd=PROJECT_ROOT)  # noqa: S603
    except subprocess.CalledProcessError as e:
        print(f'Error building binary: {e}')
        sys.exit(1)

    binary_path = DIST_DIR / binary_name
    if binary_path.exists():
        size_mb = binary_path.stat().st_size / (1024 * 1024)
        print('\nBinary built successfully!')
        print(f'Location: {binary_path}')
        print(f'Size: {size_mb:.2f} MB')
    else:
        print(f'Error: Binary not found at expected location: {binary_path}')
        sys.exit(1)


def main() -> None:
    """Build standalone binary for current platform."""
    print('=' * 60)
    print('KB-Dashboard Binary Builder')
    print('=' * 60)

    try:
        subprocess.run(['pyinstaller', '--version'], check=True, capture_output=True)  # noqa: S607
    except (subprocess.CalledProcessError, FileNotFoundError):
        print('Error: PyInstaller not found.')
        print('Install it with: pip install pyinstaller')
        sys.exit(1)

    clean_build_artifacts()
    build_binary()

    print('\n' + '=' * 60)
    print('Build complete!')
    print('=' * 60)


if __name__ == '__main__':
    main()
