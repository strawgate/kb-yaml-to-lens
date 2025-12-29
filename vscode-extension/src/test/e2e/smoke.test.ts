import { expect } from 'chai';
import {
    VSBrowser,
    WebDriver,
    Workbench
} from 'vscode-extension-tester';

/**
 * Smoke Tests - Basic verification that the extension loads and commands are registered
 *
 * These tests verify the extension doesn't crash on installation and that basic
 * commands are available. They don't test full functionality - just that the
 * extension is working at a basic level.
 */
describe('Extension Smoke Tests', function() {
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

    it('should have extension commands registered', async function() {
        this.timeout(30000);

        // Try to execute a command - if it doesn't exist, this will throw
        // We don't need a file open, we just need to verify the command exists
        try {
            await workbench.executeCommand('YAML Dashboard: Compile Dashboard');
            await driver.sleep(1000);

            // Command executed - verify we got some notification (even if it's an error)
            const notifications = await workbench.getNotifications();

            // We expect at least one notification (could be error about no file, which is fine)
            expect(notifications.length).to.be.greaterThan(0);

            // Clear notifications
            for (const notif of notifications) {
                try {
                    await notif.dismiss();
                } catch {
                    // Ignore
                }
            }
        } catch (error) {
            // If command doesn't exist, test fails
            throw new Error(`Extension command not found: ${error}`);
        }
    });

    it('should execute compile command without crashing', async function() {
        this.timeout(30000);

        await workbench.executeCommand('YAML Dashboard: Compile Dashboard');
        await driver.sleep(2000);

        // Should get a notification (likely error about no active file, which is expected)
        const notifications = await workbench.getNotifications();

        // As long as we got some response, the command didn't crash
        expect(notifications.length).to.be.greaterThan(0);

        // Clear notifications
        for (const notif of notifications) {
            try {
                await notif.dismiss();
            } catch {
                // Ignore
            }
        }
    });

    it('should execute export command without crashing', async function() {
        this.timeout(30000);

        await workbench.executeCommand('YAML Dashboard: Export Dashboard to NDJSON');
        await driver.sleep(2000);

        // Should get a notification (likely error, which is expected without a file)
        const notifications = await workbench.getNotifications();
        expect(notifications.length).to.be.greaterThan(0);

        // Clear notifications
        for (const notif of notifications) {
            try {
                await notif.dismiss();
            } catch {
                // Ignore
            }
        }
    });

    it('should execute preview command without crashing', async function() {
        this.timeout(30000);

        await workbench.executeCommand('YAML Dashboard: Preview Dashboard');
        await driver.sleep(2000);

        // Should get a notification (likely error, which is expected without a file)
        const notifications = await workbench.getNotifications();
        expect(notifications.length).to.be.greaterThan(0);

        // Clear notifications
        for (const notif of notifications) {
            try {
                await notif.dismiss();
            } catch {
                // Ignore
            }
        }
    });

    it('should execute grid editor command without crashing', async function() {
        this.timeout(30000);

        await workbench.executeCommand('YAML Dashboard: Edit Dashboard Layout');
        await driver.sleep(2000);

        // Should get a notification (likely error, which is expected without a file)
        const notifications = await workbench.getNotifications();
        expect(notifications.length).to.be.greaterThan(0);

        // Clear notifications
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
