# VSCode Extension Testing

This document describes the testing infrastructure for the YAML Dashboard Compiler VSCode extension.

## Test Philosophy

We focus on **high-value, maintainable tests** that validate business logic and catch real bugs:

- ✅ **Python tests**: Test core functionality (YAML parsing, grid updates, error handling)
- ❌ **Low-value smoke tests**: Avoid tests that only check if classes/functions exist without validating behavior

## Test Structure

### Python Tests

Located in `python/test_*.py`, these test the Python scripts that handle YAML manipulation:

- `test_grid_extractor.py` - Tests for extracting grid layout information from YAML files
- `test_grid_updater.py` - Tests for updating grid coordinates in YAML files

**Running Python tests:**

```bash
# From repository root
make test-extension-python

# Or directly with pytest
uv run python -m pytest vscode-extension/python/test_*.py -v
```

## Running Tests

```bash
# Run all tests including extension Python tests
make check

# Run only extension Python tests
make test-extension-python
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

### Import Errors

If you see import errors about `dashboard_compiler`, ensure the main package is installed:

```bash
uv sync --group dev
```
