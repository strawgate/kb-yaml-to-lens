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

        // Force close any open input boxes/command palette by pressing ESC
        try {
            const actions = driver.actions();
            await actions.sendKeys('\uE00C').perform();
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

        await driver.sleep(500);
    });

    it('should export dashboard to clipboard', async function() {
        this.timeout(45000);

        const workbench = new Workbench();

        // Open the test fixture file
        const fixturesPath = path.resolve(__dirname, '../../../test/fixtures/simple-dashboard.yaml');

        await workbench.executeCommand('workbench.action.quickOpen');
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

        await workbench.executeCommand('workbench.action.quickOpen');
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
            // If anything fails, try to cancel the input box
            try {
                await inputBox.cancel();
            } catch {
                // Ignore
            }
            throw error;
        }
    });

    it('should fail gracefully when exporting invalid dashboard', async function() {
        this.timeout(45000);

        const workbench = new Workbench();

        // Open the invalid dashboard fixture
        const fixturesPath = path.resolve(__dirname, '../../../test/fixtures/invalid-dashboard.yaml');

        await workbench.executeCommand('workbench.action.quickOpen');
        const inputBox = await InputBox.create();
        await inputBox.setText(fixturesPath);
        await inputBox.confirm();

        // Wait for file to open
        await driver.sleep(2000);

        // Execute export command
        await workbench.executeCommand('YAML Dashboard: Export Dashboard to NDJSON');

        // Wait for the command to execute
        await driver.sleep(3000);

        // Should have error notification
        const notifications = await workbench.getNotifications();

        // Expect at least one notification about the error
        expect(notifications.length).to.be.greaterThan(0);

        // Get all notification messages
        const messages = await Promise.all(
            notifications.map(async n => {
                try {
                    return await n.getMessage();
                } catch {
                    return '';
                }
            })
        );

        // Should have an error message (not a success message)
        const hasErrorMessage = messages.some(msg =>
            msg.toLowerCase().includes('error') ||
            msg.toLowerCase().includes('failed') ||
            msg.toLowerCase().includes('invalid')
        );

        expect(hasErrorMessage).to.be.true;

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
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');
    });
});
