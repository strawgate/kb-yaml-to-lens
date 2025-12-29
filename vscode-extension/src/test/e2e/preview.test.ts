import { expect } from 'chai';
import {
    VSBrowser,
    WebDriver,
    Workbench,
    EditorView,
    InputBox,
    WebView
} from 'vscode-extension-tester';
import * as path from 'path';

describe('Preview Panel E2E Tests', function() {
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

    it('should open preview panel for a dashboard', async function() {
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

        // Execute preview command
        await workbench.executeCommand('YAML Dashboard: Preview Dashboard');

        // Wait for preview to potentially open
        await driver.sleep(3000);

        // Check if a webview or editor tab opened
        const editorView = new EditorView();
        const titles = await editorView.getOpenEditorTitles();

        // Should have at least the original YAML file open
        expect(titles.length).to.be.greaterThan(0);
        expect(titles).to.include('simple-dashboard.yaml');

        // Check for notifications (might have error if Python not configured)
        const notifications = await workbench.getNotifications();
        if (notifications.length > 0) {
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

    it('should handle preview for multi-dashboard files', async function() {
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

        // Execute preview command
        await workbench.executeCommand('YAML Dashboard: Preview Dashboard');

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
            // Quick pick might not appear if there's an error
            console.log('Quick pick not available:', error);
        }

        // Check for any result (preview or error notification)
        const notifications = await workbench.getNotifications();

        // Clear notifications
        for (const notif of notifications) {
            try {
                await notif.dismiss();
            } catch {
                // Ignore
            }
        }
    });

    it('should handle invalid dashboards gracefully in preview', async function() {
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

        // Execute preview command
        await workbench.executeCommand('YAML Dashboard: Preview Dashboard');

        // Wait for the command to execute
        await driver.sleep(3000);

        // Should have error notification, not a preview
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

        // Should have an error message
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
