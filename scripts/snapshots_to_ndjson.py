import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Add project root to sys.path to allow importing dashboard_compiler
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

SNAPSHOT_DIR = project_root / 'tests' / '__snapshots__' / 'test_compiler'
OUTPUT_FILE = project_root / 'kibana_import.ndjson'


def read_and_compress_snapshot(snapshot_path: Path) -> str | None:
    """Read a Syrupy JSON snapshot file, parses it, and returns it as a compressed JSON string.

    Args:
        snapshot_path: Path to the JSON snapshot file.

    Returns:
        The compressed JSON content as a string, or None if reading/parsing fails.

    """
    try:
        with Path(snapshot_path).open('r') as f:
            dashboard_obj: Any = json.load(f)

        return json.dumps(dashboard_obj, separators=(',', ':'))

    except json.JSONDecodeError:
        msg = f'Warning: Skipping invalid JSON in {snapshot_path}'
        logger.warning(msg)
        return None
    except Exception as e:
        msg = f'Warning: Error processing {snapshot_path}: {e}'
        logger.warning(msg)
        return None


def main() -> None:
    """Find snapshots, compress them, and write the NDJSON file."""
    if not SNAPSHOT_DIR.is_dir():
        msg = f'Error: Snapshot directory not found: {SNAPSHOT_DIR}'
        logger.error(msg)
        sys.exit(1)

    ndjson_lines: list[str] = []
    snapshot_files: list[Path] = sorted(SNAPSHOT_DIR.glob('*.json'))  # Ensure consistent order

    if len(snapshot_files) == 0:
        msg = f'Warning: No snapshot files found in {SNAPSHOT_DIR}'
        logger.warning(msg)
        sys.exit(1)

    for snapshot_file in snapshot_files:
        msg = f'Processing: {snapshot_file.name}'
        logger.info(msg)
        compressed_content = read_and_compress_snapshot(snapshot_file)
        if compressed_content is not None:
            ndjson_lines.append(compressed_content)  # Add the compressed JSON string

    if len(ndjson_lines) > 0:
        try:
            with Path(OUTPUT_FILE).open('w') as f:
                f.writelines(line + '\n' for line in ndjson_lines)  # Use '\n' for actual newline
            msg = f'Successfully wrote compressed NDJSON output to: {OUTPUT_FILE}'
            logger.info(msg)
        except OSError as e:
            msg = f'Error: Could not write to output file {OUTPUT_FILE}: {e}'
            logger.exception(msg)
            sys.exit(1)
    else:
        logger.info('No valid snapshots found to generate NDJSON.')


if __name__ == '__main__':
    main()
