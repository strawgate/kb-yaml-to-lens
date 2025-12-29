# E2E Tests for VSCode Extension

This directory contains end-to-end (e2e) tests for the YAML Dashboard Compiler VSCode extension.

## Overview

These tests use [vscode-extension-tester](https://github.com/redhat-developer/vscode-extension-tester) to test the extension in a real VSCode environment. The framework:

- Downloads and runs VSCode
- Installs the extension
- Simulates user interactions (opening files, running commands, etc.)
- Validates UI behavior and notifications

## Test Files

- `activation.test.ts` - Tests extension activation and command registration
- `compile.test.ts` - Tests the compile dashboard command
- `preview.test.ts` - Tests the preview dashboard command
- `gridEditor.test.ts` - Tests the grid layout editor
- `export.test.ts` - Tests exporting dashboards to NDJSON

## Running Tests

### Prerequisites

1. Install dependencies:
   ```bash
   cd vscode-extension
   npm install
   ```

2. Compile the extension:
   ```bash
   npm run compile
   ```

3. Setup test environment (first time only):
   ```bash
   npm run test:e2e-setup
   ```
   This downloads VSCode and ChromeDriver.

### Run Tests

```bash
# Run all e2e tests
npm run test:e2e

# Run only the compiled tests
npm run test:e2e-run
```

## Test Fixtures

Test fixtures are located in `vscode-extension/test/fixtures/`:

- `simple-dashboard.yaml` - Basic single dashboard for testing core functionality
- `multi-dashboard.yaml` - File with multiple dashboards for testing selection UI
- `invalid-dashboard.yaml` - Malformed dashboard for testing error handling

## Writing Tests

### Basic Structure

```typescript
import { expect } from 'chai';
import {
    VSBrowser,
    WebDriver,
    Workbench,
    InputBox
} from 'vscode-extension-tester';

describe('My Feature Tests', function() {
    this.timeout(60000); // E2E tests need longer timeouts

    let driver: WebDriver;
    let browser: VSBrowser;

    before(async () => {
        browser = VSBrowser.instance;
        driver = browser.driver;
    });

    beforeEach(async () => {
        // Clean state before each test
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');
        await driver.sleep(500);
    });

    it('should do something', async function() {
        this.timeout(45000);

        const workbench = new Workbench();
        // ... test implementation
    });

    after(async () => {
        // Cleanup after all tests
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');
    });
});
```

### Best Practices

1. **Generous Timeouts**: E2E tests can be slow
   - Suite timeout: 60000ms (60s)
   - Individual test timeout: 30000-45000ms

2. **Clean State**: Always clean up before and after tests
   ```typescript
   await workbench.executeCommand('workbench.action.closeAllEditors');
   ```

3. **Wait for Async Operations**: Use `driver.sleep()` for UI updates
   ```typescript
   await driver.sleep(2000); // Wait 2s for file to open
   ```

4. **Handle Errors Gracefully**: Wrap potentially failing operations
   ```typescript
   try {
       await notif.dismiss();
   } catch {
       // Ignore dismiss errors
   }
   ```

5. **Test Real Workflows**: Simulate actual user behavior
   - Open files
   - Execute commands
   - Interact with quick picks
   - Verify notifications

6. **Use Test Fixtures**: Don't rely on external files
   ```typescript
   const fixturesPath = path.resolve(__dirname, '../../../test/fixtures/simple-dashboard.yaml');
   ```

## CI Integration

E2E tests run in GitHub Actions on:
- Ubuntu (with Xvfb for headless display)
- Windows
- macOS

See `.github/workflows/test-vscode-extension.yml` for the CI configuration.

## Troubleshooting

### Tests Won't Start

```bash
# Re-run setup
npm run test:e2e-setup
```

### Tests Hang

1. Check if VSCode is actually running
2. Look for error messages in console output
3. Increase timeouts if needed

### Linux Headless Issues

Ensure Xvfb is running:
```bash
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=':99.0'
```

### Platform-Specific Failures

- Use `path.resolve()` for cross-platform path handling
- Add appropriate waits for slower CI environments
- Check CI logs for specific error messages

## Resources

- [vscode-extension-tester Documentation](https://github.com/redhat-developer/vscode-extension-tester)
- [vscode-extension-tester API](https://github.com/redhat-developer/vscode-extension-tester/wiki)
- [VSCode Extension Testing Guide](https://code.visualstudio.com/api/working-with-extensions/testing-extension)
