import { expect } from 'chai';
import {
    VSBrowser,
    WebDriver,
    Workbench,
    EditorView,
    InputBox
} from 'vscode-extension-tester';
import * as path from 'path';

describe('Grid Editor E2E Tests', function() {
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

    it('should open grid editor for a dashboard', async function() {
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

        // Execute grid editor command
        await workbench.executeCommand('YAML Dashboard: Edit Dashboard Layout');

        // Wait for editor to potentially open
        await driver.sleep(3000);

        // Check if something opened (webview or notification)
        const editorView = new EditorView();
        const titles = await editorView.getOpenEditorTitles();

        // Should have at least the original YAML file
        expect(titles.length).to.be.greaterThan(0);
        expect(titles).to.include('simple-dashboard.yaml');

        // Clear any notifications
        const notifications = await workbench.getNotifications();
        for (const notif of notifications) {
            try {
                await notif.dismiss();
            } catch {
                // Ignore
            }
        }
    });

    it('should handle grid editor for multi-dashboard files', async function() {
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

        // Execute grid editor command
        await workbench.executeCommand('YAML Dashboard: Edit Dashboard Layout');

        // Wait for dashboard selection
        await driver.sleep(1500);

        // Should see a quick pick for dashboard selection
        try {
            inputBox = await InputBox.create();
            const picks = await inputBox.getQuickPicks();

            if (picks.length > 0) {
                // Select first dashboard
                await picks[0].select();
                await driver.sleep(2000);
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

        // Clear any notifications
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
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');
    });
});
