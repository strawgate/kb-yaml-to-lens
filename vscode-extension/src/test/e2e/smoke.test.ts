import { expect } from 'chai';
import * as path from 'path';
import {
    VSBrowser,
    WebDriver,
    Workbench,
    EditorView
} from 'vscode-extension-tester';

/**
 * Smoke Tests - Basic verification that the extension loads and commands execute
 *
 * These tests verify the extension activates, can open files, and commands execute
 * successfully. They test basic functionality to ensure the extension works after installation.
 */
describe('Extension Smoke Tests', function() {
    this.timeout(60000);

    let driver: WebDriver;
    let browser: VSBrowser;
    let workbench: Workbench;

    // Path to test fixtures
    const fixturesPath = path.join(__dirname, '..', '..', '..', 'test', 'fixtures');
    const simpleDashboardPath = path.join(fixturesPath, 'simple-dashboard.yaml');

    before(async function() {
        this.timeout(60000);
        browser = VSBrowser.instance;
        driver = browser.driver;
        workbench = new Workbench();

        // Wait for VSCode to be ready
        await driver.sleep(2000);

        // Verify workbench is accessible
        let retries = 10;
        while (retries > 0) {
            try {
                await driver.getTitle();
                break;
            } catch (error) {
                retries--;
                if (retries === 0) {
                    throw new Error(`VSCode not ready: ${error}`);
                }
                await driver.sleep(1000);
            }
        }
    });

    beforeEach(async () => {
        // Clear any open editors
        try {
            await workbench.executeCommand('workbench.action.closeAllEditors');
            await driver.sleep(500);
        } catch {
            // Ignore errors
        }

        // Clear notifications
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
            // Ignore
        }
    });

    /**
     * Helper to check if a notification with specific text exists
     */
    async function hasNotificationWithText(text: string): Promise<boolean> {
        try {
            const notifications = await workbench.getNotifications();
            for (const notif of notifications) {
                const message = await notif.getMessage();
                if (message.toLowerCase().includes(text.toLowerCase())) {
                    return true;
                }
            }
        } catch {
            // Ignore errors reading notifications
        }
        return false;
    }

    /**
     * Helper to open a file in the editor using VSCode's open command
     */
    async function openFile(filePath: string): Promise<void> {
        // Use VSCode's built-in open command - this works reliably in tests
        await workbench.executeCommand(`vscode.open ${filePath}`);
        await driver.sleep(2000); // Wait for file to open and extension to activate

        // Verify an editor is now active
        const editorView = new EditorView();
        const activeEditor = await editorView.getActiveTab();
        expect(activeEditor, 'File should be open in editor').to.not.be.undefined;
    }

    it('should compile dashboard successfully', async function() {
        this.timeout(20000);

        // Open the test fixture file
        await openFile(simpleDashboardPath);

        // Execute compile command
        await workbench.executeCommand('YAML Dashboard: Compile Dashboard');
        await driver.sleep(2000);

        // Should get success notification
        const hasSuccess = await hasNotificationWithText('compiled successfully');
        expect(hasSuccess, 'Expected success notification after compilation').to.be.true;
    });

    it('should export dashboard to NDJSON', async function() {
        this.timeout(20000);

        // Open the test fixture file
        await openFile(simpleDashboardPath);

        // Execute export command
        await workbench.executeCommand('YAML Dashboard: Export Dashboard to NDJSON');
        await driver.sleep(2000);

        // Should get success notification about clipboard
        const hasSuccess = await hasNotificationWithText('copied to clipboard');
        expect(hasSuccess, 'Expected success notification after export').to.be.true;
    });

    it('should open preview panel', async function() {
        this.timeout(20000);

        // Open the test fixture file
        await openFile(simpleDashboardPath);

        // Execute preview command
        await workbench.executeCommand('YAML Dashboard: Preview Dashboard');
        await driver.sleep(2000);

        // Verify preview panel opened (no error notification)
        const hasError = await hasNotificationWithText('error');
        expect(hasError, 'Preview should open without errors').to.be.false;
    });

    it('should open grid editor panel', async function() {
        this.timeout(20000);

        // Open the test fixture file
        await openFile(simpleDashboardPath);

        // Execute grid editor command
        await workbench.executeCommand('YAML Dashboard: Edit Dashboard Layout');
        await driver.sleep(2000);

        // Verify grid editor opened (no error notification)
        const hasError = await hasNotificationWithText('error');
        expect(hasError, 'Grid editor should open without errors').to.be.false;
    });
});
