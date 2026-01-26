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
    'pyproject.toml': 'toml',
    'packages/kb-dashboard-core/pyproject.toml': 'toml',
    'packages/kb-dashboard-cli/pyproject.toml': 'toml',
    'packages/kb-dashboard-tools/pyproject.toml': 'toml',
    'packages/kb-dashboard-lint/pyproject.toml': 'toml',
    'packages/kb-dashboard-docs/pyproject.toml': 'toml',
    'packages/vscode-extension/package.json': 'json',
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


def check_all_dependencies_pinned(root: Path) -> None:
    """Check that all internal package dependencies are pinned (have version specifiers)."""
    internal_packages = ['kb-dashboard-core', 'kb-dashboard-tools', 'kb-dashboard-lint', 'kb-dashboard-cli']
    
    # Files that might have internal dependencies
    files_with_deps = [
        'packages/kb-dashboard-tools/pyproject.toml',
        'packages/kb-dashboard-lint/pyproject.toml',
        'packages/kb-dashboard-cli/pyproject.toml',
        'packages/kb-dashboard-docs/pyproject.toml',
        'pyproject.toml',
    ]
    
    unpinned_deps = []
    
    for file_path in files_with_deps:
        full_path = root / file_path
        if not full_path.exists():
            continue
            
        content = full_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            # Skip name fields
            if 'name =' in line:
                continue
            
            for pkg in internal_packages:
                # Check for unpinned dependency: "pkg" followed by comma or closing bracket
                # But not "pkg==" or "pkg>=" or "pkg<=" etc.
                unpinned_pattern = re.compile(r'"' + re.escape(pkg) + r'"(?=\s*[,)])')
                if unpinned_pattern.search(line) and '==' not in line and '>=' not in line and '<=' not in line and '~=' not in line and '!=' not in line:
                    unpinned_deps.append((file_path, line_num, pkg))
    
    if unpinned_deps:
        click.echo('\nError: Found unpinned internal package dependencies:', err=True)
        for file_path, line_num, pkg in unpinned_deps:
            click.echo(f'  {file_path}:{line_num} - "{pkg}" is not pinned', err=True)
        click.echo('\nAll internal package dependencies must be pinned with a version (e.g., "pkg==1.0.0")', err=True)
        raise click.ClickException('Unpinned dependencies found')


def update_internal_dependencies(root: Path, old_version: str, new_version: str, dry_run: bool) -> None:
    """Update internal package dependencies to exact versions."""
    internal_packages = ['kb-dashboard-core', 'kb-dashboard-tools', 'kb-dashboard-lint', 'kb-dashboard-cli']
    
    # Files that might have internal dependencies
    files_with_deps = [
        'packages/kb-dashboard-tools/pyproject.toml',
        'packages/kb-dashboard-lint/pyproject.toml',
        'packages/kb-dashboard-cli/pyproject.toml',
        'packages/kb-dashboard-docs/pyproject.toml',
        'pyproject.toml',
    ]
    
    click.echo('\nUpdating internal package dependencies...')
    
    for file_path in files_with_deps:
        full_path = root / file_path
        if not full_path.exists():
            continue
            
        content = full_path.read_text(encoding='utf-8')
        updated = False
        new_content = content
        
        for pkg in internal_packages:
            # Only match pinned dependencies (safe - won't match name fields):
            # "kb-dashboard-core==0.1.10",
            # "kb-dashboard-core>=0.1.10",
            
            # Pattern 1: Pinned to old version (safe to replace directly - won't match name field)
            pinned_pattern = f'"{pkg}=={old_version}"'
            if pinned_pattern in new_content:
                new_content = new_content.replace(pinned_pattern, f'"{pkg}=={new_version}"')
                updated = True
            
            # Pattern 2: Minimum version (safe to replace directly - won't match name field)
            min_version_pattern = f'"{pkg}>={old_version}"'
            if min_version_pattern in new_content:
                new_content = new_content.replace(min_version_pattern, f'"{pkg}=={new_version}"')
                updated = True
        
        if updated:
            if not dry_run:
                full_path.write_text(new_content, encoding='utf-8')
            status = '(dry-run)' if dry_run else 'OK'
            click.echo(f'  {file_path}: internal deps -> {new_version} {status}')


def update_versions(new_version: str, dry_run: bool) -> None:
    """Update version in all version files."""
    root = get_project_root()

    # Determine current version from canonical source
    canonical_path = root / 'packages/kb-dashboard-cli/pyproject.toml'
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

    # Check that all internal dependencies are pinned before updating
    check_all_dependencies_pinned(root)
    
    # Update internal package dependencies
    if not dry_run:
        update_internal_dependencies(root, current_version, new_version, dry_run)
    else:
        click.echo('\nWould update internal package dependencies...')
        update_internal_dependencies(root, current_version, new_version, dry_run)

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
        
        # Update CLI uv.lock (workspace uses root lock, but keep for compatibility)
        # Note: In a workspace, uv.lock is managed at root, but we check CLI directory
        cli_dir = root / 'packages/kb-dashboard-cli'
        try:
            # In workspace mode, uv lock should be run from root
            # But we verify the CLI directory exists
            if cli_dir.exists():
                click.echo('  Note: Using root workspace uv.lock (packages/kb-dashboard-cli is a workspace member)')
            else:
                click.echo('  Warning: packages/kb-dashboard-cli directory not found', err=True)
        except Exception as e:
            click.echo(f'  Warning: Failed to verify CLI directory: {e}', err=True)

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
    current = read_version(root / 'packages/kb-dashboard-cli/pyproject.toml', 'toml')
    new_version = bump_version(current, 'patch')
    update_versions(new_version, dry_run)


@cli.command()
@click.option('--dry-run', is_flag=True, help='Preview changes without applying them.')
def minor(dry_run: bool) -> None:
    """Bump minor version (0.1.1 -> 0.2.0)."""
    root = get_project_root()
    current = read_version(root / 'packages/kb-dashboard-cli/pyproject.toml', 'toml')
    new_version = bump_version(current, 'minor')
    update_versions(new_version, dry_run)


@cli.command()
@click.option('--dry-run', is_flag=True, help='Preview changes without applying them.')
def major(dry_run: bool) -> None:
    """Bump major version (0.1.1 -> 1.0.0)."""
    root = get_project_root()
    current = read_version(root / 'packages/kb-dashboard-cli/pyproject.toml', 'toml')
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
