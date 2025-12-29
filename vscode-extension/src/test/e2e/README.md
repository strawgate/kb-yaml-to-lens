# E2E Smoke Tests for VSCode Extension

This directory contains basic smoke tests for the YAML Dashboard Compiler VSCode extension.

## Overview

These tests use [vscode-extension-tester](https://github.com/redhat-developer/vscode-extension-tester) to verify the extension loads and doesn't crash after installation. The tests:

- Download and run VSCode
- Install the extension
- Execute commands to verify they're registered
- Validate that commands don't crash (even if they return errors)

**Note:** These are smoke tests, not comprehensive functional tests. They verify the extension works at a basic level, not that all features work perfectly.

## Test Files

- `smoke.test.ts` - Basic tests that verify extension commands are registered and don't crash

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

## Test Approach

These smoke tests verify the extension doesn't crash on basic operations:

1. **Commands are registered** - VSCode can find the extension's commands
2. **Commands execute** - Running a command doesn't throw an exception
3. **Extension responds** - Commands provide feedback (notifications)

Tests intentionally run commands without opening files first. This means commands will return error notifications (e.g., "No active YAML file"), which is expected and acceptable for smoke tests.

## Writing Smoke Tests

### Basic Structure

```typescript
import { expect } from 'chai';
import {
    VSBrowser,
    WebDriver,
    Workbench
} from 'vscode-extension-tester';

describe('My Smoke Tests', function() {
    this.timeout(60000);

    let driver: WebDriver;
    let browser: VSBrowser;
    let workbench: Workbench;

    before(async () => {
        browser = VSBrowser.instance;
        driver = browser.driver;
        workbench = new Workbench();
    });

    beforeEach(async () => {
        // Clean state before each test
        await workbench.executeCommand('workbench.action.closeAllEditors');
        await driver.sleep(500);
    });

    it('should execute command without crashing', async function() {
        this.timeout(30000);

        await workbench.executeCommand('My Command');
        await driver.sleep(2000);

        // Verify we got a notification (even if it's an error)
        const notifications = await workbench.getNotifications();
        expect(notifications.length).to.be.greaterThan(0);
    });
});
```

### Best Practices for Smoke Tests

1. **Keep it simple** - Don't test full functionality, just that commands execute
2. **Expect errors** - Commands may fail without proper context (files open, etc.)
3. **Avoid complex UI interactions** - No InputBox, QuickPick, or file opening
4. **Test command registration** - Verify commands exist and are callable
5. **Minimal assertions** - Just check that something happened (notification appeared)

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
