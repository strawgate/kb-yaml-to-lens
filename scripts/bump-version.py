#!/usr/bin/env python3
"""Bump version across all project components.

This script updates version numbers in all project component files atomically,
ensuring consistency across the Python compiler, VS Code extension, fixture
generator, and root project.

Usage:
    python scripts/bump-version.py patch              # 0.1.1 -> 0.1.2
    python scripts/bump-version.py minor              # 0.1.1 -> 0.2.0
    python scripts/bump-version.py major              # 0.1.1 -> 1.0.0
    python scripts/bump-version.py --set 1.0.0        # Set explicit version
    python scripts/bump-version.py --show             # Show current version
    python scripts/bump-version.py patch --dry-run    # Preview changes
    python scripts/bump-version.py patch --commit     # Create git commit
    python scripts/bump-version.py patch --tag        # Create git tag
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Version file locations relative to project root
VERSION_FILES: dict[str, tuple[str, list[str]]] = {
    'compiler/pyproject.toml': ('toml', ['project', 'version']),
    'vscode-extension/package.json': ('json', ['version']),
    'fixture-generator/package.json': ('json', ['version']),
    'pyproject.toml': ('toml', ['project', 'version']),
}

# ANSI color codes for terminal output
COLORS = {
    'green': '\033[92m',
    'yellow': '\033[93m',
    'red': '\033[91m',
    'blue': '\033[94m',
    'reset': '\033[0m',
    'bold': '\033[1m',
}


def colored(text: str, color: str) -> str:
    """Return colored text for terminal output."""
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def get_project_root() -> Path:
    """Get the project root directory."""
    script_path = Path(__file__).resolve()
    return script_path.parent.parent


def parse_semver(version: str) -> tuple[int, int, int]:
    """Parse a semantic version string into (major, minor, patch) tuple.

    Args:
        version: Version string like "1.2.3"

    Returns:
        Tuple of (major, minor, patch) integers

    Raises:
        ValueError: If version format is invalid
    """
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version)
    if not match:
        msg = f"Invalid version format: '{version}'. Expected format: X.Y.Z"
        raise ValueError(msg)
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def format_semver(major: int, minor: int, patch: int) -> str:
    """Format a semantic version tuple as a string."""
    return f'{major}.{minor}.{patch}'


def bump_version(version: str, bump_type: str) -> str:
    """Bump a semantic version by the specified type.

    Args:
        version: Current version string
        bump_type: One of 'major', 'minor', or 'patch'

    Returns:
        New version string
    """
    major, minor, patch = parse_semver(version)

    if bump_type == 'major':
        return format_semver(major + 1, 0, 0)
    if bump_type == 'minor':
        return format_semver(major, minor + 1, 0)
    if bump_type == 'patch':
        return format_semver(major, minor, patch + 1)

    msg = f"Invalid bump type: '{bump_type}'. Expected: major, minor, or patch"
    raise ValueError(msg)


def read_toml_version(path: Path, keys: list[str]) -> str:
    """Read version from a TOML file.

    Args:
        path: Path to the TOML file
        keys: List of keys to traverse (e.g., ['project', 'version'])

    Returns:
        Version string
    """
    content = path.read_text()
    # Simple regex-based TOML parsing for [project] version = "X.Y.Z"
    # This avoids needing tomllib for writing and handles our specific case
    if keys == ['project', 'version']:
        match = re.search(r'^\[project\]\s*\n(?:.*\n)*?version\s*=\s*"([^"]+)"', content, re.MULTILINE)
        if match:
            return match.group(1)
    msg = f"Could not find version in {path}"
    raise ValueError(msg)


def write_toml_version(path: Path, keys: list[str], new_version: str) -> None:
    """Write version to a TOML file.

    Args:
        path: Path to the TOML file
        keys: List of keys to traverse (e.g., ['project', 'version'])
        new_version: New version string to write
    """
    content = path.read_text()
    if keys == ['project', 'version']:
        # Replace version in [project] section
        new_content = re.sub(
            r'(^\[project\]\s*\n(?:.*\n)*?version\s*=\s*)"([^"]+)"',
            rf'\g<1>"{new_version}"',
            content,
            count=1,
            flags=re.MULTILINE,
        )
        if new_content == content:
            msg = f"Failed to update version in {path}"
            raise ValueError(msg)
        path.write_text(new_content)
        return
    msg = f"Unsupported TOML key path: {keys}"
    raise ValueError(msg)


def read_json_version(path: Path, keys: list[str]) -> str:
    """Read version from a JSON file.

    Args:
        path: Path to the JSON file
        keys: List of keys to traverse (e.g., ['version'])

    Returns:
        Version string
    """
    data = json.loads(path.read_text())
    value: Any = data
    for key in keys:
        value = value[key]
    return str(value)


def write_json_version(path: Path, keys: list[str], new_version: str) -> None:
    """Write version to a JSON file preserving formatting.

    Args:
        path: Path to the JSON file
        keys: List of keys to traverse (e.g., ['version'])
        new_version: New version string to write
    """
    content = path.read_text()
    data = json.loads(content)

    # Navigate to parent and set the version
    target = data
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = new_version

    # Detect indentation from original file
    indent = 2  # default
    if match := re.search(r'\n(\s+)"', content):
        indent = len(match.group(1))

    # Write with same formatting
    path.write_text(json.dumps(data, indent=indent) + '\n')


def read_version(path: Path, file_format: str, keys: list[str]) -> str:
    """Read version from a file.

    Args:
        path: Path to the file
        file_format: Either 'toml' or 'json'
        keys: List of keys to traverse

    Returns:
        Version string
    """
    if file_format == 'toml':
        return read_toml_version(path, keys)
    if file_format == 'json':
        return read_json_version(path, keys)
    msg = f"Unsupported format: {file_format}"
    raise ValueError(msg)


def write_version(path: Path, file_format: str, keys: list[str], new_version: str) -> None:
    """Write version to a file.

    Args:
        path: Path to the file
        file_format: Either 'toml' or 'json'
        keys: List of keys to traverse
        new_version: New version string to write
    """
    if file_format == 'toml':
        write_toml_version(path, keys, new_version)
    elif file_format == 'json':
        write_json_version(path, keys, new_version)
    else:
        msg = f"Unsupported format: {file_format}"
        raise ValueError(msg)


def get_current_versions(root: Path) -> dict[str, str]:
    """Get current versions from all version files.

    Args:
        root: Project root directory

    Returns:
        Dict mapping file path to version string
    """
    versions = {}
    for file_path, (file_format, keys) in VERSION_FILES.items():
        full_path = root / file_path
        if full_path.exists():
            versions[file_path] = read_version(full_path, file_format, keys)
        else:
            versions[file_path] = '(file not found)'
    return versions


def get_canonical_version(root: Path) -> str:
    """Get the canonical version from compiler/pyproject.toml.

    Args:
        root: Project root directory

    Returns:
        Current version string
    """
    file_path = 'compiler/pyproject.toml'
    file_format, keys = VERSION_FILES[file_path]
    return read_version(root / file_path, file_format, keys)


def check_git_clean(root: Path) -> bool:
    """Check if git working directory is clean.

    Args:
        root: Project root directory

    Returns:
        True if clean, False otherwise
    """
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and not result.stdout.strip()


def update_all_versions(root: Path, new_version: str, *, dry_run: bool = False) -> list[tuple[str, str, str]]:
    """Update version in all version files.

    Args:
        root: Project root directory
        new_version: New version string
        dry_run: If True, don't actually write changes

    Returns:
        List of (file_path, old_version, new_version) tuples
    """
    changes = []

    for file_path, (file_format, keys) in VERSION_FILES.items():
        full_path = root / file_path
        if not full_path.exists():
            print(f"{colored('⚠', 'yellow')} Skipping {file_path} (file not found)")
            continue

        old_version = read_version(full_path, file_format, keys)
        changes.append((file_path, old_version, new_version))

        if not dry_run:
            write_version(full_path, file_format, keys, new_version)

    return changes


def create_git_commit(root: Path, version: str) -> bool:
    """Create a git commit with the version bump.

    Args:
        root: Project root directory
        version: New version string

    Returns:
        True if successful, False otherwise
    """
    # Stage version files
    files_to_stage = [f for f in VERSION_FILES if (root / f).exists()]
    result = subprocess.run(
        ['git', 'add', *files_to_stage],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"{colored('✗', 'red')} Failed to stage files: {result.stderr}")
        return False

    # Create commit
    result = subprocess.run(
        ['git', 'commit', '-m', f'chore: Bump version to {version}'],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"{colored('✗', 'red')} Failed to create commit: {result.stderr}")
        return False

    print(f"{colored('✓', 'green')} Created commit: chore: Bump version to {version}")
    return True


def create_git_tag(root: Path, version: str) -> bool:
    """Create a git tag for the version.

    Args:
        root: Project root directory
        version: Version string

    Returns:
        True if successful, False otherwise
    """
    tag_name = f'v{version}'
    result = subprocess.run(
        ['git', 'tag', tag_name],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"{colored('✗', 'red')} Failed to create tag: {result.stderr}")
        return False

    print(f"{colored('✓', 'green')} Created tag: {tag_name}")
    return True


def main() -> int:
    """Run the version bump script."""
    parser = argparse.ArgumentParser(
        description='Bump version across all project components',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s patch              Bump patch version (0.1.1 -> 0.1.2)
  %(prog)s minor              Bump minor version (0.1.1 -> 0.2.0)
  %(prog)s major              Bump major version (0.1.1 -> 1.0.0)
  %(prog)s --set 1.0.0        Set explicit version
  %(prog)s --show             Show current versions
  %(prog)s patch --dry-run    Preview changes without applying
  %(prog)s patch --commit     Create git commit after bump
  %(prog)s patch --tag        Create git tag after bump
""",
    )

    parser.add_argument(
        'bump_type',
        nargs='?',
        choices=['major', 'minor', 'patch'],
        help='Type of version bump',
    )
    parser.add_argument(
        '--set',
        dest='set_version',
        metavar='VERSION',
        help='Set explicit version (e.g., 1.0.0)',
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help='Show current versions and exit',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them',
    )
    parser.add_argument(
        '--commit',
        action='store_true',
        help='Create git commit after bumping version',
    )
    parser.add_argument(
        '--tag',
        action='store_true',
        help='Create git tag after bumping version',
    )

    args = parser.parse_args()
    root = get_project_root()

    # Show current versions
    if args.show:
        print(f"{colored('Current versions:', 'bold')}")
        versions = get_current_versions(root)
        for file_path, version in versions.items():
            print(f"  {file_path}: {colored(version, 'blue')}")
        return 0

    # Validate arguments
    if not args.bump_type and not args.set_version:
        parser.error('Must specify bump type (major/minor/patch) or --set VERSION')

    if args.bump_type and args.set_version:
        parser.error('Cannot specify both bump type and --set VERSION')

    # Determine new version
    current_version = get_canonical_version(root)

    if args.set_version:
        # Validate the explicit version
        try:
            parse_semver(args.set_version)
        except ValueError as e:
            print(f"{colored('✗', 'red')} {e}")
            return 1
        new_version = args.set_version
    else:
        new_version = bump_version(current_version, args.bump_type)

    # Check git status if committing
    if args.commit and not args.dry_run:
        if not check_git_clean(root):
            print(f"{colored('⚠', 'yellow')} Git working directory has uncommitted changes.")
            print('  Commit or stash changes first, or use --dry-run to preview.')
            return 1

    # Preview or apply changes
    action = 'Would update' if args.dry_run else 'Updating'
    print(f"{colored(f'{action} version: {current_version} → {new_version}', 'bold')}")
    print()

    changes = update_all_versions(root, new_version, dry_run=args.dry_run)

    for file_path, old_ver, new_ver in changes:
        status = '(dry-run)' if args.dry_run else colored('✓', 'green')
        if old_ver == new_ver:
            print(f"  {status} {file_path}: {old_ver} (unchanged)")
        else:
            print(f"  {status} {file_path}: {old_ver} → {new_ver}")

    if args.dry_run:
        print()
        print(f"{colored('Dry run complete. No files were modified.', 'yellow')}")
        return 0

    print()

    # Create git commit if requested
    if args.commit:
        if not create_git_commit(root, new_version):
            return 1

    # Create git tag if requested
    if args.tag:
        if not create_git_tag(root, new_version):
            return 1

    print(f"{colored('✓', 'green')} Version bump complete!")

    if not args.commit:
        print()
        print('Next steps:')
        print(f"  git add {' '.join(f for f in VERSION_FILES if (root / f).exists())}")
        print(f'  git commit -m "chore: Bump version to {new_version}"')
        if not args.tag:
            print(f'  git tag v{new_version}')
        print('  git push origin main && git push origin --tags')

    return 0


if __name__ == '__main__':
    sys.exit(main())
