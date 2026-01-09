#!/usr/bin/env python3
"""Bump version across all project components.

Updates version numbers in all project component files atomically.

Usage:
    python scripts/bump-version.py patch          # 0.1.1 -> 0.1.2
    python scripts/bump-version.py minor          # 0.1.1 -> 0.2.0
    python scripts/bump-version.py major          # 0.1.1 -> 1.0.0
    python scripts/bump-version.py --set 1.0.0    # Set explicit version
    python scripts/bump-version.py --show         # Show current versions
    python scripts/bump-version.py patch --dry-run # Preview changes
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

# Version file locations relative to project root
VERSION_FILES = {
    'compiler/pyproject.toml': 'toml',
    'vscode-extension/package.json': 'json',
    'fixture-generator/package.json': 'json',
    'pyproject.toml': 'toml',
}


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).resolve().parent.parent


def parse_semver(version: str) -> tuple[int, int, int]:
    """Parse a semantic version string into (major, minor, patch) tuple."""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version)
    if not match:
        raise ValueError(f"Invalid version format: '{version}'. Expected: X.Y.Z")
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
    if file_format == 'toml':
        data = tomllib.loads(path.read_text())
        return data['project']['version']
    # json
    data = json.loads(path.read_text())
    return data['version']


def write_version(path: Path, file_format: str, old_version: str, new_version: str) -> None:
    """Write version to a file."""
    content = path.read_text()
    if file_format == 'toml':
        # Replace version = "old" with version = "new" in TOML
        new_content = content.replace(f'version = "{old_version}"', f'version = "{new_version}"', 1)
    else:
        # Replace "version": "old" with "version": "new" in JSON
        new_content = content.replace(f'"version": "{old_version}"', f'"version": "{new_version}"', 1)
    if new_content == content:
        raise ValueError(f'Failed to update version in {path}')
    path.write_text(new_content)


def main() -> int:
    """Run the version bump script."""
    parser = argparse.ArgumentParser(description='Bump version across all project components')
    parser.add_argument('bump_type', nargs='?', choices=['major', 'minor', 'patch'], help='Type of version bump')
    parser.add_argument('--set', dest='set_version', metavar='VERSION', help='Set explicit version (e.g., 1.0.0)')
    parser.add_argument('--show', action='store_true', help='Show current versions and exit')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying them')
    args = parser.parse_args()

    root = get_project_root()

    # Show current versions
    if args.show:
        print('Current versions:')
        for file_path, file_format in VERSION_FILES.items():
            full_path = root / file_path
            if full_path.exists():
                version = read_version(full_path, file_format)
                print(f'  {file_path}: {version}')
        return 0

    # Validate arguments
    if not args.bump_type and not args.set_version:
        parser.error('Must specify bump type (major/minor/patch) or --set VERSION')
    if args.bump_type and args.set_version:
        parser.error('Cannot specify both bump type and --set VERSION')

    # Determine new version from canonical source
    canonical_path = root / 'compiler/pyproject.toml'
    current_version = read_version(canonical_path, 'toml')

    if args.set_version:
        parse_semver(args.set_version)  # Validate format
        new_version = args.set_version
    else:
        new_version = bump_version(current_version, args.bump_type)

    # Update all files
    action = 'Would update' if args.dry_run else 'Updating'
    print(f'{action} version: {current_version} -> {new_version}')

    for file_path, file_format in VERSION_FILES.items():
        full_path = root / file_path
        if not full_path.exists():
            print(f'  Skipping {file_path} (not found)')
            continue
        old_ver = read_version(full_path, file_format)
        if not args.dry_run:
            write_version(full_path, file_format, old_ver, new_version)
        status = '(dry-run)' if args.dry_run else 'OK'
        print(f'  {file_path}: {old_ver} -> {new_version} {status}')

    if args.dry_run:
        print('\nDry run complete. No files were modified.')
    else:
        print('\nVersion bump complete!')

    return 0


if __name__ == '__main__':
    sys.exit(main())
