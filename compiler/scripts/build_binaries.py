#!/usr/bin/env python3
"""Build standalone binaries for kb-dashboard using PyInstaller."""

import argparse
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


def build_cli_binary(platform_name: str) -> Path:
    """Build the CLI binary."""
    binary_name = f'kb-dashboard-{platform_name}'
    if platform.system() == 'Windows':
        binary_name += '.exe'

    print(f'Building CLI binary: {binary_name}...')

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
    print(f'Built CLI binary: {binary_path} ({size_mb:.1f} MB)')
    return binary_path


def build_lsp_binary() -> Path:
    """Build the LSP server binary."""
    binary_name = 'kb-dashboard-compiler-lsp'
    if platform.system() == 'Windows':
        binary_name += '.exe'

    print(f'Building LSP binary: {binary_name}...')

    # Build with PyInstaller
    lsp_path = COMPILER_ROOT / 'src' / 'dashboard_compiler' / 'lsp' / 'server.py'
    subprocess.run(  # noqa: S603
        ['pyinstaller', '--name', binary_name, '--onefile', '--clean', '--noconfirm', str(lsp_path)],  # noqa: S607
        check=True,
        cwd=COMPILER_ROOT,
    )

    # Report success
    binary_path = COMPILER_ROOT / 'dist' / binary_name
    size_mb = binary_path.stat().st_size / (1024 * 1024)
    print(f'Built LSP binary: {binary_path} ({size_mb:.1f} MB)')
    return binary_path


def main() -> None:
    """Build standalone binaries for current platform."""
    parser = argparse.ArgumentParser(description='Build standalone binaries using PyInstaller')
    parser.add_argument(
        'binary_type',
        choices=['cli', 'lsp', 'all'],
        default='all',
        nargs='?',
        help='Type of binary to build (default: all)',
    )
    args = parser.parse_args()

    platform_name = get_platform_name()
    print(f'Building binaries for platform: {platform_name}')

    # Clean previous builds
    for d in ['build', 'dist']:
        path = COMPILER_ROOT / d
        if path.exists():
            shutil.rmtree(path)

    # Build requested binaries
    if args.binary_type in ('cli', 'all'):
        build_cli_binary(platform_name)

    if args.binary_type in ('lsp', 'all'):
        build_lsp_binary()

    print('All requested binaries built successfully!')


if __name__ == '__main__':
    main()
