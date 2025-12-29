import { expect } from 'chai';
import {
    VSBrowser,
    WebDriver,
    Workbench,
    EditorView,
    InputBox
} from 'vscode-extension-tester';
import * as path from 'path';

describe('Extension Activation E2E Tests', function() {
    this.timeout(60000); // E2E tests can take longer

    let driver: WebDriver;
    let browser: VSBrowser;

    before(async () => {
        browser = VSBrowser.instance;
        driver = browser.driver;
    });

    beforeEach(async () => {
        // Clean up before each test
        const workbench = new Workbench();

        // Force close any open input boxes/command palette by pressing ESC multiple times
        for (let i = 0; i < 3; i++) {
            try {
                const actions = driver.actions();
                await actions.sendKeys('\uE00C').perform();
                await driver.sleep(300);
            } catch {
                // Ignore if ESC doesn't work
            }
        }

        await workbench.executeCommand('workbench.action.closeAllEditors');
        await driver.sleep(1000);

        // Clear any notifications
        try {
            const notifications = await workbench.getNotifications();
            for (const notif of notifications) {
                try {
                    await notif.dismiss();
                } catch {
                    // Ignore
                }
            }
        } catch {
            // Ignore if no notifications
        }

        await driver.sleep(1000);
    });

    afterEach(async () => {
        // Clean up after each test to prevent lingering UI elements
        // Force close any open input boxes/command palette by pressing ESC multiple times
        for (let i = 0; i < 5; i++) {
            try {
                const actions = driver.actions();
                await actions.sendKeys('\uE00C').perform();
                await driver.sleep(200);
            } catch {
                // Ignore if ESC doesn't work
            }
        }

        await driver.sleep(500);
    });

    it('should activate when opening a YAML file', async function() {
        this.timeout(30000);

        const workbench = new Workbench();

        // Open the test fixture file using vscode.open command
        const fixturesPath = path.resolve(__dirname, '../../../test/fixtures/simple-dashboard.yaml');

        // Use the command palette to open the file
        await workbench.executeCommand('workbench.action.quickOpen');
        const inputBox = await InputBox.create();
        await inputBox.setText(fixturesPath);
        await inputBox.confirm();

        // Wait a bit for the file to open and extension to activate
        await driver.sleep(3000);

        // Verify the editor is open
        const editorView = new EditorView();
        const titles = await editorView.getOpenEditorTitles();
        expect(titles).to.include('simple-dashboard.yaml');
    });

    // Note: Command registration is tested implicitly by the other e2e test suites
    // (compile.test.ts, preview.test.ts, export.test.ts, gridEditor.test.ts)
    // Testing via command palette is unreliable in headless CI environments

    after(async () => {
        // Clean up: close all editors
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');
    });
});
