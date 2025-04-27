import json
import sys
from pathlib import Path

# Add project root to sys.path to allow importing dashboard_compiler
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

SNAPSHOT_DIR = project_root / "tests" / "__snapshots__" / "test_compiler"
OUTPUT_FILE = project_root / "kibana_import.ndjson"


def read_and_compress_snapshot(snapshot_path: Path) -> str | None:
    """
    Reads a Syrupy JSON snapshot file, parses it, and returns it
    as a compressed JSON string.

    Args:
        snapshot_path: Path to the JSON snapshot file.

    Returns:
        The compressed JSON content as a string, or None if reading/parsing fails.
    """
    try:
        with open(snapshot_path) as f:
            # Read and parse the JSON object
            dashboard_obj = json.load(f)

        # Re-serialize with compact separators for NDJSON
        compressed_json = json.dumps(dashboard_obj, separators=(",", ":"))
        return compressed_json

    except json.JSONDecodeError:
        print(f"Warning: Skipping invalid JSON in {snapshot_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Warning: Error processing {snapshot_path}: {e}", file=sys.stderr)
        return None


def main():
    """
    Main function to find snapshots, compress them, and write the NDJSON file.
    """
    if not SNAPSHOT_DIR.is_dir():
        print(f"Error: Snapshot directory not found: {SNAPSHOT_DIR}", file=sys.stderr)
        sys.exit(1)

    ndjson_lines = []
    snapshot_files = sorted(SNAPSHOT_DIR.glob("*.json"))  # Ensure consistent order

    if not snapshot_files:
        print(f"Warning: No snapshot files found in {SNAPSHOT_DIR}", file=sys.stderr)

    for snapshot_file in snapshot_files:
        print(f"Processing: {snapshot_file.name}")
        compressed_content = read_and_compress_snapshot(snapshot_file)
        if compressed_content:
            ndjson_lines.append(compressed_content)  # Add the compressed JSON string

    if ndjson_lines:
        try:
            # Write each compressed JSON object followed by a newline character
            with open(OUTPUT_FILE, "w") as f:
                for line in ndjson_lines:
                    f.write(line + "\n")  # Use '\n' for actual newline
            print(f"Successfully wrote compressed NDJSON output to: {OUTPUT_FILE}")
        except OSError as e:
            print(
                f"Error: Could not write to output file {OUTPUT_FILE}: {e}",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        print("No valid snapshots found to generate NDJSON.")


if __name__ == "__main__":
    main()
