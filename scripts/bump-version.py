#!/usr/bin/env python3
"""Bump version across all project components.

Updates version numbers in all project component files.

Usage:
    python scripts/bump-version.py show              # Show current versions
    python scripts/bump-version.py patch             # 0.1.1 -> 0.1.2
    python scripts/bump-version.py minor             # 0.1.1 -> 0.2.0
    python scripts/bump-version.py major             # 0.1.1 -> 1.0.0
    python scripts/bump-version.py set 1.0.0         # Set explicit version
    python scripts/bump-version.py patch --dry-run   # Preview changes
"""



import json
import re
import subprocess
import tomllib
from pathlib import Path

import click

# Version file locations relative to project root
VERSION_FILES = {
    'packages/kb-dashboard-compiler/pyproject.toml': 'toml',
    'packages/vscode-extension/package.json': 'json',
    'pyproject.toml': 'toml',
}


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).resolve().parent.parent


def parse_semver(version: str) -> tuple[int, int, int]:
    """Parse a semantic version string into (major, minor, patch) tuple."""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version)
    if not match:
        raise click.BadParameter(f"Invalid version format: '{version}'. Expected: X.Y.Z")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(version: str, bump_type: str) -> str:
    """Bump a semantic version by the specified type."""
    major, minor, patch = parse_semver(version)
    if bump_type == 'major':
        return f'{major + 1}.0.0'
    if bump_type == 'minor':
        return f'{major}.{minor + 1}.0'
    return f'{major}.{minor}.{patch + 1}'


def read_version(path: Path, file_format: str) -> str:
    """Read version from a file."""
    try:
        if file_format == 'toml':
            data = tomllib.loads(path.read_text(encoding='utf-8'))
            return data['project']['version']
        # json
        data = json.loads(path.read_text(encoding='utf-8'))
        return data['version']
    except KeyError as e:
        raise click.ClickException(f'Missing version key in {path}: {e}') from e


def write_version(path: Path, file_format: str, old_version: str, new_version: str) -> None:
    """Write version to a file."""
    content = path.read_text(encoding='utf-8')
    if file_format == 'toml':
        new_content = content.replace(f'version = "{old_version}"', f'version = "{new_version}"', 1)
    else:
        new_content = content.replace(f'"version": "{old_version}"', f'"version": "{new_version}"', 1)
    if new_content == content:
        msg = f'Failed to update version in {path}'
        raise click.ClickException(msg)
    path.write_text(new_content, encoding='utf-8')


def update_versions(new_version: str, dry_run: bool) -> None:
    """Update version in all version files."""
    root = get_project_root()

    # Determine current version from canonical source
    canonical_path = root / 'packages/kb-dashboard-compiler/pyproject.toml'
    current_version = read_version(canonical_path, 'toml')

    action = 'Would update' if dry_run else 'Updating'
    click.echo(f'{action} version: {current_version} -> {new_version}')

    package_json_updated = False
    pyproject_updated = False
    for file_path, file_format in VERSION_FILES.items():
        full_path = root / file_path
        if not full_path.exists():
            click.echo(f'  Skipping {file_path} (not found)')
            continue
        old_ver = read_version(full_path, file_format)
        if not dry_run:
            write_version(full_path, file_format, old_ver, new_version)
        status = '(dry-run)' if dry_run else 'OK'
        click.echo(f'  {file_path}: {old_ver} -> {new_version} {status}')
        
        if file_path == 'packages/vscode-extension/package.json':
            package_json_updated = True
        if file_path.endswith('pyproject.toml'):
            pyproject_updated = True

    # Update package-lock.json by running npm install
    if package_json_updated and not dry_run:
        click.echo('\nUpdating package-lock.json...')
        vscode_ext_dir = root / 'packages/vscode-extension'
        try:
            subprocess.run(
                ['npm', 'install', '--package-lock-only'],
                cwd=vscode_ext_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            click.echo('  packages/vscode-extension/package-lock.json: updated')
        except subprocess.CalledProcessError as e:
            click.echo(f'  Warning: Failed to update package-lock.json: {e.stderr}', err=True)
        except FileNotFoundError:
            click.echo('  Warning: npm not found. Skipping package-lock.json update.', err=True)

    # Update uv.lock files by running uv lock
    if pyproject_updated and not dry_run:
        click.echo('\nUpdating uv.lock files...')
        
        # Update root uv.lock
        try:
            subprocess.run(
                ['uv', 'lock'],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
            click.echo('  uv.lock: updated')
        except subprocess.CalledProcessError as e:
            click.echo(f'  Warning: Failed to update root uv.lock: {e.stderr}', err=True)
        except FileNotFoundError:
            click.echo('  Warning: uv not found. Skipping uv.lock update.', err=True)
        
        # Update compiler uv.lock
        compiler_dir = root / 'packages/kb-dashboard-compiler'
        try:
            subprocess.run(
                ['uv', 'lock'],
                cwd=compiler_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            click.echo('  packages/kb-dashboard-compiler/uv.lock: updated')
        except subprocess.CalledProcessError as e:
            click.echo(f'  Warning: Failed to update packages/kb-dashboard-compiler/uv.lock: {e.stderr}', err=True)
        except FileNotFoundError:
            click.echo('  Warning: uv not found. Skipping packages/kb-dashboard-compiler/uv.lock update.', err=True)

    if dry_run:
        click.echo('\nDry run complete. No files were modified.')
        if package_json_updated:
            click.echo('  (package-lock.json would also be updated)')
        if pyproject_updated:
            click.echo('  (uv.lock files would also be updated)')
    else:
        click.echo('\nVersion bump complete!')


@click.group()
def cli() -> None:
    """Bump version across all project components."""


@cli.command()
def show() -> None:
    """Show current versions across all components."""
    root = get_project_root()
    click.echo('Current versions:')
    for file_path, file_format in VERSION_FILES.items():
        full_path = root / file_path
        if full_path.exists():
            version = read_version(full_path, file_format)
            click.echo(f'  {file_path}: {version}')


@cli.command()
@click.option('--dry-run', is_flag=True, help='Preview changes without applying them.')
def patch(dry_run: bool) -> None:
    """Bump patch version (0.1.1 -> 0.1.2)."""
    root = get_project_root()
    current = read_version(root / 'packages/kb-dashboard-compiler/pyproject.toml', 'toml')
    new_version = bump_version(current, 'patch')
    update_versions(new_version, dry_run)


@cli.command()
@click.option('--dry-run', is_flag=True, help='Preview changes without applying them.')
def minor(dry_run: bool) -> None:
    """Bump minor version (0.1.1 -> 0.2.0)."""
    root = get_project_root()
    current = read_version(root / 'packages/kb-dashboard-compiler/pyproject.toml', 'toml')
    new_version = bump_version(current, 'minor')
    update_versions(new_version, dry_run)


@cli.command()
@click.option('--dry-run', is_flag=True, help='Preview changes without applying them.')
def major(dry_run: bool) -> None:
    """Bump major version (0.1.1 -> 1.0.0)."""
    root = get_project_root()
    current = read_version(root / 'packages/kb-dashboard-compiler/pyproject.toml', 'toml')
    new_version = bump_version(current, 'major')
    update_versions(new_version, dry_run)


@cli.command('set')
@click.argument('version')
@click.option('--dry-run', is_flag=True, help='Preview changes without applying them.')
def set_version(version: str, dry_run: bool) -> None:
    """Set explicit version (e.g., 1.0.0)."""
    parse_semver(version)  # Validate format
    update_versions(version, dry_run)


if __name__ == '__main__':
    cli()
