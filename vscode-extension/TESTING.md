# VSCode Extension Testing

This document describes the testing infrastructure for the YAML Dashboard Compiler VSCode extension.

## Test Philosophy

We focus on **high-value, maintainable tests** that validate business logic and catch real bugs:

- ✅ **Python tests**: Test core functionality (YAML parsing, grid updates, error handling)
- ✅ **E2E tests**: Test extension activation, commands, and user workflows in VSCode
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

### E2E Tests

Located in `src/test/e2e/*.test.ts`, these test the extension running in VSCode:

- `activation.test.ts` - Tests extension activation and command registration
- `compile.test.ts` - Tests the compile dashboard command
- `preview.test.ts` - Tests the preview dashboard command
- `gridEditor.test.ts` - Tests the grid editor command
- `export.test.ts` - Tests the export to NDJSON command

**Running E2E tests:**

```bash
# From vscode-extension directory
npm run test:e2e

# Or setup and run separately
npm run test:e2e-setup  # Downloads VSCode and ChromeDriver (first time only)
npm run test:e2e-run    # Runs the tests
```

**Test fixtures** are located in `test/fixtures/`:
- `simple-dashboard.yaml` - Basic single dashboard
- `multi-dashboard.yaml` - Multiple dashboards for testing selection
- `invalid-dashboard.yaml` - Malformed dashboard for error testing

## Running Tests

```bash
# Run all tests including extension Python tests
make check

# Run only extension Python tests
make test-extension-python

# Run only extension E2E tests
cd vscode-extension && npm run test:e2e
```

## Continuous Integration

Extension tests are run in CI when changes are made to the `vscode-extension/` directory:

- **Python tests**: Run on every PR/push on `ubuntu-latest`
- **TypeScript compilation and linting**: Run on every PR/push on `ubuntu-latest`
- **E2E tests**: Run on every PR/push on `ubuntu-latest`, `windows-latest`, and `macos-latest`

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

### E2E Tests

Follow the existing pattern in the e2e test files:

```typescript
import { expect } from 'chai';
import {
    VSBrowser,
    WebDriver,
    Workbench,
    InputBox
} from 'vscode-extension-tester';

describe('My Feature E2E Tests', function() {
    this.timeout(60000);

    let driver: WebDriver;
    let browser: VSBrowser;

    before(async () => {
        browser = VSBrowser.instance;
        driver = browser.driver;
    });

    beforeEach(async () => {
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');
        await driver.sleep(500);
    });

    it('should do something', async function() {
        this.timeout(45000);

        const workbench = new Workbench();

        // Test implementation
        // ...

        expect(result).to.be.true;
    });

    after(async () => {
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');
    });
});
```

**E2E Test Best Practices:**

1. **Use generous timeouts**: E2E tests can be slow, especially in CI
2. **Clean up state**: Close all editors before and after tests
3. **Wait for async operations**: Use `driver.sleep()` to wait for UI updates
4. **Handle errors gracefully**: Use try/catch for operations that might fail
5. **Test realistic workflows**: Simulate what users actually do
6. **Use test fixtures**: Create dedicated YAML files in `test/fixtures/`

## Test Coverage

Current test coverage:

**Python Tests:**
- ✅ Grid extraction from YAML files
- ✅ Grid coordinate updates
- ✅ YAML formatting preservation
- ✅ Error handling for missing files
- ✅ Invalid input handling
- ✅ Input validation (panel IDs, grid coordinates)
- ✅ Path traversal prevention

**E2E Tests:**
- ✅ Extension activation when opening YAML files
- ✅ Command registration (compile, preview, export, grid editor)
- ✅ Compile command execution
- ✅ Multi-dashboard selection workflow
- ✅ Preview panel opening
- ✅ Grid editor opening
- ✅ Export to clipboard functionality

### What We Test

Focus on **business logic**, **security**, and **user workflows**:

**Python:**
- Core functionality (parsing, updating YAML)
- Edge cases (missing fields, invalid data)
- Security (input validation, path checks)
- Error handling (file not found, parse errors)

**E2E:**
- Extension activation and lifecycle
- Command execution and user interactions
- Multi-step workflows (dashboard selection, compilation)
- Error handling and notifications
- Cross-platform compatibility (Linux, Windows, macOS)

### What We Don't Test

We avoid low-value tests like:

- Simple class instantiation checks
- Tests that just verify a module can be imported
- Tests that don't validate actual behavior
- Detailed webview rendering (covered by browser testing if needed)

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

### E2E Tests Fail to Start

If E2E tests fail with "Cannot find VSCode":

```bash
# Setup VSCode and ChromeDriver
cd vscode-extension
npm run test:e2e-setup
```

### E2E Tests Hang or Timeout

If tests hang:

1. **Linux**: Ensure Xvfb is running for headless testing
   ```bash
   Xvfb :99 -screen 0 1024x768x24 &
   export DISPLAY=':99.0'
   ```

2. **Increase timeouts**: E2E tests can be slow, especially on CI
3. **Check logs**: Look for error messages in the test output

### E2E Tests Fail on Specific Platform

E2E tests run on Linux, Windows, and macOS in CI. Platform-specific failures might indicate:

- Path separator issues (use `path.resolve()` consistently)
- Display/windowing issues (ensure proper headless setup)
- Timing issues (add appropriate waits for UI updates)
