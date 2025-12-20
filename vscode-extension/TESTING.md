# VSCode Extension Testing

This document describes the testing infrastructure for the YAML Dashboard Compiler VSCode extension.

## Test Structure

The extension has two types of tests:

### 1. Python Tests

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

### 2. TypeScript Tests

Located in `src/test/`, these test the TypeScript modules:

- `unit/compiler.test.ts` - Tests for the DashboardCompiler class
- `unit/gridEditorPanel.test.ts` - Tests for the GridEditorPanel class
- `unit/previewPanel.test.ts` - Tests for the PreviewPanel class
- `unit/fileWatcher.test.ts` - Tests for the file watcher setup

**Running TypeScript tests:**

```bash
# From vscode-extension directory
npm test

# Or run only unit tests
npm run test:unit

# From repository root
make test-extension
```

## Running All Tests

To run all extension tests (both Python and TypeScript):

```bash
# From repository root
make check
```

This will run:
1. Python linting and formatting
2. Python unit tests
3. Python smoke tests
4. VSCode extension Python tests

## Continuous Integration

The extension tests are integrated into the CI pipeline:

### Manual Setup Required

Due to GitHub Actions permissions, the CI workflow file must be manually added:

1. Copy `vscode-extension/proposed-ci-workflow.yml` to `.github/workflows/test-vscode-extension.yml`
2. Commit and push the changes

The CI workflow will:
- Run Python tests for the extension scripts
- Compile TypeScript code
- Run TypeScript linting
- Run TypeScript unit tests

### Triggered By

The CI workflow runs when:
- Code is pushed to `main` or `develop` branches
- Pull requests target `main` or `develop` branches
- Changes are made to files in the `vscode-extension/` directory

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

### TypeScript Tests

Follow the Mocha test pattern:

```typescript
import * as assert from 'assert';

suite('MyFeature Tests', () => {
    test('should do something', () => {
        // Test implementation
        assert.strictEqual(actual, expected);
    });
});
```

## Test Coverage

Current test coverage focuses on:

- ✅ Grid extraction from YAML files
- ✅ Grid coordinate updates
- ✅ YAML formatting preservation
- ✅ Error handling for missing files
- ✅ Invalid input handling
- ✅ Basic module loading and structure

Areas for future improvement:

- Integration tests with VSCode API
- Webview rendering tests
- End-to-end workflow tests
- Performance tests for large dashboards

## Troubleshooting

### Python Tests Fail

If Python tests fail with import errors:

```bash
# Ensure dashboard_compiler is installed
uv sync --all-extras
```

### TypeScript Tests Fail

If TypeScript tests fail:

```bash
cd vscode-extension
npm install
npm run compile
npm test
```

### CI Workflow Not Running

Ensure:
1. The workflow file is in `.github/workflows/` (not in `vscode-extension/`)
2. The file is committed to the repository
3. Changes were made to `vscode-extension/` directory
