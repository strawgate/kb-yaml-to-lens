#!/usr/bin/env python3
"""Build standalone LSP server binary using PyInstaller."""

import platform
import shutil
import subprocess
from pathlib import Path

VSCODE_ROOT = Path(__file__).parent.parent
PROJECT_ROOT = VSCODE_ROOT.parent


def get_platform_name() -> str:
    """Get platform name for binary naming (e.g., 'linux-x64', 'darwin-arm64')."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if machine in ('x86_64', 'amd64'):
        arch = 'x64'
    elif machine in ('aarch64', 'arm64'):
        arch = 'arm64'
    else:
        msg = f'Unsupported architecture: {machine}'
        raise ValueError(msg)

    return f'{system}-{arch}'


def main() -> None:
    """Build standalone LSP server binary for current platform."""
    platform_name = get_platform_name()
    binary_name = 'dashboard-compiler-lsp'
    if platform.system() == 'Windows':
        binary_name += '.exe'

    print(f'Building LSP server binary for {platform_name}...')

    # Output directory for platform-specific binary
    output_dir = VSCODE_ROOT / 'bin' / platform_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clean previous builds
    for d in ['build', 'dist']:
        path = VSCODE_ROOT / d
        if path.exists():
            shutil.rmtree(path)

    # Build with PyInstaller using the module entry point
    # Find pyinstaller executable
    pyinstaller_path = shutil.which('pyinstaller')
    if pyinstaller_path is None:
        msg = 'pyinstaller not found in PATH. Install with: pip install pyinstaller'
        raise RuntimeError(msg)

    # PyInstaller can bundle Python modules directly using -m flag
    # This uses the kb-dashboard-lsp entry point from pyproject.toml
    subprocess.run(  # noqa: S603
        [
            pyinstaller_path,
            '--name',
            binary_name,
            '--onefile',
            '--clean',
            '--noconfirm',
            '-m',
            'dashboard_compiler.lsp.server',
        ],
        check=True,
        cwd=VSCODE_ROOT,
    )

    # Move binary to bin/{platform}/
    binary_path = VSCODE_ROOT / 'dist' / binary_name
    target_path = output_dir / binary_name
    shutil.move(binary_path, target_path)

    # Clean build artifacts
    for d in ['build', 'dist']:
        path = VSCODE_ROOT / d
        if path.exists():
            shutil.rmtree(path)

    # Report success
    size_mb = target_path.stat().st_size / (1024 * 1024)
    print(f'Built: {target_path} ({size_mb:.1f} MB)')


if __name__ == '__main__':
    main()
