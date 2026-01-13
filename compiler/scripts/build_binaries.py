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


def build_binary(binary_name: str) -> Path:
    """Build a binary with the specified name.

    Args:
        binary_name: Name for the output binary (without .exe extension on Windows)

    Returns:
        Path to the built binary
    """
    if platform.system() == 'Windows':
        binary_name += '.exe'

    print(f'Building binary: {binary_name}...')

    # Sync dependencies (LSP is now a main dependency, no extra group needed)
    subprocess.run(['uv', 'sync', '--group', 'build'], check=True, cwd=COMPILER_ROOT)  # noqa: S607

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
    print(f'Built binary: {binary_path} ({size_mb:.1f} MB)')
    return binary_path


def build_cli_binary(platform_name: str) -> Path:
    """Build the unified CLI binary with LSP support."""
    binary_name = f'kb-dashboard-{platform_name}'
    return build_binary(binary_name)


def build_lsp_binary() -> Path:
    """Build the LSP binary for VS Code extension.

    This builds the same unified binary but with a fixed name expected by the
    VS Code extension workflow.
    """
    return build_binary('kb-dashboard-compiler-lsp')


def main() -> None:
    """Build standalone binaries for current platform."""
    parser = argparse.ArgumentParser(description='Build standalone binaries for kb-dashboard')
    parser.add_argument(
        '--lsp',
        action='store_true',
        help='Build LSP binary for VS Code extension (kb-dashboard-compiler-lsp)',
    )
    args = parser.parse_args()

    # Clean previous builds
    for d in ['build', 'dist']:
        path = COMPILER_ROOT / d
        if path.exists():
            shutil.rmtree(path)

    if args.lsp:
        print('Building LSP binary for VS Code extension...')
        build_lsp_binary()
        print('LSP binary built successfully!')
    else:
        platform_name = get_platform_name()
        print(f'Building unified binary for platform: {platform_name}')
        build_cli_binary(platform_name)
        print('Unified binary built successfully!')


if __name__ == '__main__':
    main()
