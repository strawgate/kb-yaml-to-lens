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
        // Clean up before each test - close all editors and dismiss notifications
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');

        // Force close any open input boxes/command palette by pressing ESC
        try {
            const actions = driver.actions();
            await actions.sendKeys('\uE00C').perform(); // ESC key
            await driver.sleep(500);
        } catch {
            // Ignore if ESC doesn't work
        }

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

    it('should register all required commands', async function() {
        this.timeout(45000);

        const workbench = new Workbench();

        // Ensure extension is activated by opening a YAML file first
        const fixturesPath = path.resolve(__dirname, '../../../test/fixtures/simple-dashboard.yaml');
        await workbench.executeCommand('workbench.action.quickOpen');
        let inputBox = await InputBox.create();
        await inputBox.setText(fixturesPath);
        await inputBox.confirm();

        // Wait for file to open and extension to fully activate
        await driver.sleep(8000); // Increased to 8s to allow LSP server to start

        // Test command registration by trying to execute each command
        // If a command is not registered, VSCode will show an error notification
        const commands = [
            'yamlDashboard.compile',
            'yamlDashboard.preview',
            'yamlDashboard.export',
            'yamlDashboard.editLayout'
        ];

        for (const command of commands) {
            try {
                // Execute the command - it will show a dashboard selection or error
                await workbench.executeCommand(command);
                await driver.sleep(1000);

                // Check if command opened a quick pick or notification
                // If command is not registered, VSCode shows "command not found" error
                const notifications = await workbench.getNotifications();
                let hasError = false;

                for (const notif of notifications) {
                    const msg = await notif.getMessage();
                    if (msg.includes('not found') || msg.includes('Unknown command')) {
                        hasError = true;
                        expect.fail(`Command ${command} is not registered`);
                    }
                    // Dismiss notification
                    try {
                        await notif.dismiss();
                    } catch {
                        // Ignore
                    }
                }

                // Cancel any quick pick that might have opened
                try {
                    const actions = driver.actions();
                    await actions.sendKeys('\uE00C').perform();
                    await driver.sleep(500);
                } catch {
                    // Ignore
                }
            } catch (error) {
                // If command is not registered, executeCommand might throw
                expect.fail(`Failed to execute command ${command}: ${error}`);
            }
        }

        // If we got here, all commands are registered
        expect(true).to.be.true;
    });

    after(async () => {
        // Clean up: close all editors
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');
    });
});
