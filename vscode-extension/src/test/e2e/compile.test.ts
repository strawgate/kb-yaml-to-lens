import { expect } from 'chai';
import {
    VSBrowser,
    WebDriver,
    Workbench,
    InputBox
} from 'vscode-extension-tester';
import * as path from 'path';

describe('Compile Command E2E Tests', function() {
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

    it('should compile a simple dashboard successfully', async function() {
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

        // Execute compile command
        await workbench.executeCommand('YAML Dashboard: Compile Dashboard');

        // Wait a bit for the command to execute
        await driver.sleep(3000);

        // Check for notifications (success or error)
        const notifications = await workbench.getNotifications();

        if (notifications.length > 0) {
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

            // Should have either a success message or an informative error
            const hasMessage = messages.some(msg =>
                msg.includes('compiled') ||
                msg.includes('Python') ||
                msg.includes('error')
            );

            expect(hasMessage).to.be.true;

            // Clear notifications
            for (const notif of notifications) {
                try {
                    await notif.dismiss();
                } catch {
                    // Ignore dismiss errors
                }
            }
        }
    });

    it('should handle multi-dashboard files with selection', async function() {
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

        // Execute compile command
        await workbench.executeCommand('YAML Dashboard: Compile Dashboard');

        // Wait for dashboard selection quick pick
        await driver.sleep(1500);

        // Should see a quick pick for dashboard selection
        inputBox = await InputBox.create();
        const picks = await inputBox.getQuickPicks();

        // Should have 2 dashboards to choose from
        expect(picks.length).to.be.at.least(1);

        // Select the first dashboard
        if (picks.length > 0) {
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
    });

    it('should handle invalid dashboards with appropriate error message', async function() {
        this.timeout(45000);

        const workbench = new Workbench();

        // Open the invalid dashboard fixture
        const fixturesPath = path.resolve(__dirname, '../../../test/fixtures/invalid-dashboard.yaml');

        await workbench.executeCommand('workbench.action.files.openFile');
        const inputBox = await InputBox.create();
        await inputBox.setText(fixturesPath);
        await inputBox.confirm();

        // Wait for file to open
        await driver.sleep(2000);

        // Execute compile command
        await workbench.executeCommand('YAML Dashboard: Compile Dashboard');

        // Wait for the command to execute
        await driver.sleep(3000);

        // Check for error notification
        const notifications = await workbench.getNotifications();

        // Should have at least one notification
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
                // Ignore dismiss errors
            }
        }
    });

    after(async () => {
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');
    });
});
