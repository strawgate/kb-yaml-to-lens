import { expect } from 'chai';
import {
    VSBrowser,
    WebDriver,
    Workbench
} from 'vscode-extension-tester';

/**
 * Smoke Tests - Basic verification that the extension loads and commands execute
 *
 * These are minimal tests that verify the extension activates and commands execute
 * without crashing. They don't test full functionality - just that the extension
 * installs and responds to commands.
 */
describe('Extension Smoke Tests', function() {
    this.timeout(60000);

    let driver: WebDriver;
    let browser: VSBrowser;
    let workbench: Workbench;

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

    it('should execute compile command', async function() {
        this.timeout(15000);

        // Execute compile command - should respond with error since no file is open
        await workbench.executeCommand('YAML Dashboard: Compile Dashboard');
        await driver.sleep(1500);

        // Should get an error notification (no active editor)
        const hasError = await hasNotificationWithText('error');
        expect(hasError, 'Expected error notification when no file is open').to.be.true;
    });

    it('should execute export command', async function() {
        this.timeout(15000);

        // Execute export command - should respond with error since no file is open
        await workbench.executeCommand('YAML Dashboard: Export Dashboard to NDJSON');
        await driver.sleep(1500);

        // Should get an error notification (no active editor)
        const hasError = await hasNotificationWithText('error');
        expect(hasError, 'Expected error notification when no file is open').to.be.true;
    });

    it('should execute preview command', async function() {
        this.timeout(15000);

        // Execute preview command - should respond with error since no file is open
        await workbench.executeCommand('YAML Dashboard: Preview Dashboard');
        await driver.sleep(1500);

        // Should get an error notification (no active editor)
        const hasError = await hasNotificationWithText('error');
        expect(hasError, 'Expected error notification when no file is open').to.be.true;
    });

    it('should execute grid editor command', async function() {
        this.timeout(15000);

        // Execute grid editor command - should respond with error since no file is open
        await workbench.executeCommand('YAML Dashboard: Edit Dashboard Layout');
        await driver.sleep(1500);

        // Should get an error notification (no active editor)
        const hasError = await hasNotificationWithText('error');
        expect(hasError, 'Expected error notification when no file is open').to.be.true;
    });
});
