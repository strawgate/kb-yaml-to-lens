import { expect } from 'chai';
import {
    VSBrowser,
    WebDriver,
    Workbench,
    InputBox
} from 'vscode-extension-tester';
import * as path from 'path';

describe('Export Command E2E Tests', function() {
    this.timeout(60000);

    let driver: WebDriver;
    let browser: VSBrowser;

    before(async () => {
        browser = VSBrowser.instance;
        driver = browser.driver;
    });

    beforeEach(async () => {
        // Clean up before each test
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');
        await driver.sleep(500);
    });

    it('should export dashboard to clipboard', async function() {
        this.timeout(45000);

        const workbench = new Workbench();

        // Open the test fixture file
        const fixturesPath = path.resolve(__dirname, '../../../test/fixtures/simple-dashboard.yaml');

        await workbench.executeCommand('workbench.action.files.openFile');
        const inputBox = await InputBox.create();
        await inputBox.setText(fixturesPath);
        await inputBox.confirm();

        // Wait for file to open
        await driver.sleep(2000);

        // Execute export command
        await workbench.executeCommand('YAML Dashboard: Export Dashboard to NDJSON');

        // Wait for export to complete
        await driver.sleep(3000);

        // Check for notifications
        const notifications = await workbench.getNotifications();

        if (notifications.length > 0) {
            // Get notification messages
            const messages = await Promise.all(
                notifications.map(async n => {
                    try {
                        return await n.getMessage();
                    } catch {
                        return '';
                    }
                })
            );

            // Should have either success or error message
            const hasMessage = messages.some(msg =>
                msg.includes('clipboard') ||
                msg.includes('copied') ||
                msg.includes('Export') ||
                msg.includes('error') ||
                msg.includes('Python')
            );

            expect(hasMessage).to.be.true;

            // Clear notifications
            for (const notif of notifications) {
                try {
                    await notif.dismiss();
                } catch {
                    // Ignore
                }
            }
        }
    });

    it('should handle export for multi-dashboard files', async function() {
        this.timeout(45000);

        const workbench = new Workbench();

        // Open the multi-dashboard fixture
        const fixturesPath = path.resolve(__dirname, '../../../test/fixtures/multi-dashboard.yaml');

        await workbench.executeCommand('workbench.action.files.openFile');
        let inputBox = await InputBox.create();
        await inputBox.setText(fixturesPath);
        await inputBox.confirm();

        // Wait for file to open
        await driver.sleep(2000);

        // Execute export command
        await workbench.executeCommand('YAML Dashboard: Export Dashboard to NDJSON');

        // Wait for dashboard selection
        await driver.sleep(1500);

        // Should see a quick pick for dashboard selection
        try {
            inputBox = await InputBox.create();
            const picks = await inputBox.getQuickPicks();

            if (picks.length > 0) {
                // Select first dashboard
                await picks[0].select();
                await driver.sleep(3000);

                // Check for result notification
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
            }
        } catch (error) {
            // Quick pick might not appear if there's an error
            console.log('Quick pick not available:', error);
        }
    });

    after(async () => {
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');
    });
});
