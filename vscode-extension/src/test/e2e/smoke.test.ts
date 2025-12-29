import { expect } from 'chai';
import * as path from 'path';
import {
    VSBrowser,
    WebDriver,
    Workbench,
    EditorView
} from 'vscode-extension-tester';

/**
 * Smoke Tests - Basic verification that the extension loads and commands work
 *
 * These tests verify the extension doesn't crash on installation and that basic
 * commands actually succeed (not just that they're registered). We use test fixtures
 * to verify compilation works end-to-end.
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
        this.timeout(30000);
        browser = VSBrowser.instance;
        driver = browser.driver;
        workbench = new Workbench();

        // Wait for VSCode to be fully ready
        await driver.sleep(2000);

        // Wait for workbench to be available by trying to access it
        let retries = 10;
        while (retries > 0) {
            try {
                await workbench.executeCommand('workbench.action.showCommands');
                await driver.sleep(500);
                // If we get here, workbench is ready
                // Press Escape to close the command palette
                await driver.actions().sendKeys('\u001b').perform();
                await driver.sleep(500);
                break;
            } catch (error) {
                retries--;
                if (retries === 0) {
                    throw new Error(`Workbench not ready after retries: ${error}`);
                }
                await driver.sleep(1000);
            }
        }
    });

    beforeEach(async () => {
        // Clean up before each test
        await workbench.executeCommand('workbench.action.closeAllEditors');
        await driver.sleep(500);

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

        await driver.sleep(500);
    });

    /**
     * Helper to open a YAML file without using InputBox (avoids blocking issues)
     */
    async function openFile(filePath: string): Promise<void> {
        // Use vscode.open command to open file directly
        await workbench.executeCommand(`workbench.action.quickOpen`);
        await driver.sleep(500);

        // Type the file path
        await driver.actions().sendKeys(filePath).perform();
        await driver.sleep(500);

        // Press Enter to open
        await driver.actions().sendKeys('\n').perform();
        await driver.sleep(2000); // Wait for file to open
    }

    /**
     * Helper to check if a notification with specific text exists
     */
    async function hasNotificationWithText(text: string): Promise<boolean> {
        const notifications = await workbench.getNotifications();
        for (const notif of notifications) {
            const message = await notif.getMessage();
            if (message.includes(text)) {
                return true;
            }
        }
        return false;
    }

    it('should have extension commands registered', async function() {
        this.timeout(30000);

        // Open a test file first
        await openFile(simpleDashboardPath);

        // Execute compile command
        await workbench.executeCommand('YAML Dashboard: Compile Dashboard');
        await driver.sleep(2000);

        // Should get success notification
        const hasSuccess = await hasNotificationWithText('Dashboard compiled successfully');
        expect(hasSuccess, 'Expected compilation success notification').to.be.true;

        // Clear notifications
        const notifications = await workbench.getNotifications();
        for (const notif of notifications) {
            try {
                await notif.dismiss();
            } catch {
                // Ignore
            }
        }
    });

    it('should compile dashboard successfully', async function() {
        this.timeout(30000);

        // Open test file
        await openFile(simpleDashboardPath);

        // Execute compile command
        await workbench.executeCommand('YAML Dashboard: Compile Dashboard');
        await driver.sleep(2000);

        // Verify success
        const hasSuccess = await hasNotificationWithText('Dashboard compiled successfully');
        expect(hasSuccess, 'Expected compilation success notification').to.be.true;

        // Clear notifications
        const notifications = await workbench.getNotifications();
        for (const notif of notifications) {
            try {
                await notif.dismiss();
            } catch {
                // Ignore
            }
        }
    });

    it('should export dashboard to NDJSON successfully', async function() {
        this.timeout(30000);

        // Open test file
        await openFile(simpleDashboardPath);

        // Execute export command
        await workbench.executeCommand('YAML Dashboard: Export Dashboard to NDJSON');
        await driver.sleep(2000);

        // Verify success (checks for clipboard copy message)
        const hasSuccess = await hasNotificationWithText('NDJSON copied to clipboard');
        expect(hasSuccess, 'Expected export success notification').to.be.true;

        // Clear notifications
        const notifications = await workbench.getNotifications();
        for (const notif of notifications) {
            try {
                await notif.dismiss();
            } catch {
                // Ignore
            }
        }
    });

    it('should open preview panel successfully', async function() {
        this.timeout(30000);

        // Open test file
        await openFile(simpleDashboardPath);

        // Execute preview command
        await workbench.executeCommand('YAML Dashboard: Preview Dashboard');
        await driver.sleep(3000); // Give time for preview panel to open

        // Verify preview panel opened by checking for webview
        const editorView = new EditorView();
        const openEditors = await editorView.getOpenEditorTitles();

        // Preview panel should be open (title contains "Dashboard Preview")
        const hasPreview = openEditors.some(title => title.includes('Dashboard Preview') || title.includes('Preview'));
        expect(hasPreview, 'Expected preview panel to open').to.be.true;

        // Clear notifications if any
        const notifications = await workbench.getNotifications();
        for (const notif of notifications) {
            try {
                await notif.dismiss();
            } catch {
                // Ignore
            }
        }
    });

    it('should open grid editor panel successfully', async function() {
        this.timeout(30000);

        // Open test file
        await openFile(simpleDashboardPath);

        // Execute grid editor command
        await workbench.executeCommand('YAML Dashboard: Edit Dashboard Layout');
        await driver.sleep(3000); // Give time for grid editor to open

        // Verify grid editor panel opened
        const editorView = new EditorView();
        const openEditors = await editorView.getOpenEditorTitles();

        // Grid editor should be open (title contains "Grid Editor" or similar)
        const hasGridEditor = openEditors.some(title => title.includes('Grid Editor') || title.includes('Layout'));
        expect(hasGridEditor, 'Expected grid editor panel to open').to.be.true;

        // Clear notifications if any
        const notifications = await workbench.getNotifications();
        for (const notif of notifications) {
            try {
                await notif.dismiss();
            } catch {
                // Ignore
            }
        }
    });

    after(async () => {
        // Final cleanup
        await workbench.executeCommand('workbench.action.closeAllEditors');
    });
});
