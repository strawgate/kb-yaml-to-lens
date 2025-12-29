import {
    VSBrowser,
    WebDriver,
    Workbench
} from 'vscode-extension-tester';

/**
 * Smoke Tests - Basic verification that the extension loads and commands execute
 *
 * These tests verify the extension activates and commands execute without crashing.
 * They do NOT test actual functionality - just that the extension loads successfully.
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

    it('should have extension commands registered', async function() {
        this.timeout(10000);

        // Execute compile command
        // If command doesn't exist, this will throw and test will fail
        // If command executes without crashing VSCode, test passes
        await workbench.executeCommand('YAML Dashboard: Compile Dashboard');

        // Give command time to complete
        await driver.sleep(1000);

        // If we get here, command executed successfully
    });

    it('should execute export command without crashing', async function() {
        this.timeout(10000);

        await workbench.executeCommand('YAML Dashboard: Export Dashboard to NDJSON');
        await driver.sleep(1000);
    });

    it('should execute preview command without crashing', async function() {
        this.timeout(10000);

        await workbench.executeCommand('YAML Dashboard: Preview Dashboard');
        await driver.sleep(1000);
    });

    it('should execute grid editor command without crashing', async function() {
        this.timeout(10000);

        await workbench.executeCommand('YAML Dashboard: Edit Dashboard Layout');
        await driver.sleep(1000);
    });
});
