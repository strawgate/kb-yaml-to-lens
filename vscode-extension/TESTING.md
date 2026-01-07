# VSCode Extension Testing

This document describes the testing infrastructure for the YAML Dashboard Compiler VSCode extension.

## Test Philosophy

We focus on **high-value, maintainable tests** that validate business logic and catch real bugs:

- ✅ **Python tests**: Test core functionality (YAML parsing, grid updates, error handling)
- ✅ **E2E Extension Tests**: Test the extension functionality in a real VS Code environment
- ❌ **Low-value smoke tests**: Avoid tests that only check if classes/functions exist without validating behavior

## Test Structure

### Python Tests

Located in `python/test_*.py`, these test the Python scripts that handle YAML manipulation:

- `test_grid_extractor.py` - Tests for extracting grid layout information from YAML files
- `test_grid_updater.py` - Tests for updating grid coordinates in YAML files

**Running Python tests:**

```bash
# From vscode-extension directory
make test

# Or directly with pytest from repository root
uv run python -m pytest vscode-extension/python/test_*.py -v
```

### E2E Extension Tests

Located in `src/test/suite/extension.test.ts`, these tests run the actual extension inside a VS Code instance (headless). They verify:

- The extension activates correctly
- Commands are registered
- YAML files can be opened and compiled

**Running E2E tests:**

```bash
# From vscode-extension directory
npm test
```

*Note: This requires `xvfb` to be installed on Linux environments.*

## Running Tests

```bash
# Run all extension tests (from vscode-extension directory)
make test

# Run only TypeScript unit tests (from vscode-extension directory)
make test-unit

# Run E2E tests (from vscode-extension directory)
npm test
```

## Continuous Integration

Extension tests are run in CI when changes are made to the `vscode-extension/` directory.

## Writing New Tests

### Python Tests

Follow the existing pattern in `test_grid_extractor.py`:

```python
import unittest
from pathlib import Path

class TestMyFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        pass

    def test_something(self):
        """Test description"""
        # Test implementation
        self.assertEqual(actual, expected)
```

## Test Coverage

Current test coverage:

- ✅ Grid extraction from YAML files
- ✅ Grid coordinate updates
- ✅ YAML formatting preservation
- ✅ Error handling for missing files
- ✅ Invalid input handling
- ✅ Input validation (panel IDs, grid coordinates)
- ✅ Path traversal prevention

### What We Test

Focus on **business logic** and **security**:

- Core functionality (parsing, updating YAML)
- Edge cases (missing fields, invalid data)
- Security (input validation, path checks)
- Error handling (file not found, parse errors)

### What We Don't Test

We avoid low-value tests like:

- Simple class instantiation checks
- Tests that just verify a module can be imported
- Tests that don't validate actual behavior

For TypeScript, testing VSCode webview interactions requires a full extension development environment. The Python scripts are where the core business logic lives, so that's where we focus testing efforts.

## Troubleshooting

### Python Tests Fail

If Python tests fail with import errors:

```bash
# Ensure dashboard_compiler is installed
uv sync --group dev
```

### E2E Tests Fail

If E2E tests fail with "No workspace folder found" or activation errors, ensure:

1. You are running `npm test` from the vscode-extension directory.
2. The `.venv` is created (`uv sync --group dev` from repo root).
3. `xvfb` is installed if running on Linux without a display.
