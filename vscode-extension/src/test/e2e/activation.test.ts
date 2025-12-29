import { expect } from 'chai';
import {
    VSBrowser,
    WebDriver,
    Workbench,
    EditorView,
    InputBox
} from 'vscode-extension-tester';
import * as path from 'path';

describe('Extension Activation E2E Tests', function() {
    this.timeout(60000); // E2E tests can take longer

    let driver: WebDriver;
    let browser: VSBrowser;

    before(async () => {
        browser = VSBrowser.instance;
        driver = browser.driver;
    });

    beforeEach(async () => {
        // Clean up before each test - close all editors and dismiss notifications
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');

        // Force close any open input boxes/command palette by pressing ESC
        try {
            const actions = driver.actions();
            await actions.sendKeys('\uE00C').perform(); // ESC key
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
    });

    it('should activate when opening a YAML file', async function() {
        this.timeout(30000);

        const workbench = new Workbench();

        // Open the test fixture file using vscode.open command
        const fixturesPath = path.resolve(__dirname, '../../../test/fixtures/simple-dashboard.yaml');

        // Use the command palette to open the file
        await workbench.executeCommand('workbench.action.quickOpen');
        const inputBox = await InputBox.create();
        await inputBox.setText(fixturesPath);
        await inputBox.confirm();

        // Wait a bit for the file to open and extension to activate
        await driver.sleep(3000);

        // Verify the editor is open
        const editorView = new EditorView();
        const titles = await editorView.getOpenEditorTitles();
        expect(titles).to.include('simple-dashboard.yaml');
    });

    it('should register all required commands', async function() {
        this.timeout(45000);

        const workbench = new Workbench();

        // Ensure extension is activated by opening a YAML file first
        const fixturesPath = path.resolve(__dirname, '../../../test/fixtures/simple-dashboard.yaml');
        await workbench.executeCommand('workbench.action.quickOpen');
        let inputBox = await InputBox.create();
        await inputBox.setText(fixturesPath);
        await inputBox.confirm();

        // Wait for file to open and extension to fully activate
        await driver.sleep(5000);

        // Now open command palette to search for our commands
        await workbench.executeCommand('workbench.action.showCommands');

        inputBox = await InputBox.create();

        try {
            await inputBox.setText('YAML Dashboard');
            await driver.sleep(3000); // Increased wait for command filtering

            const picks = await inputBox.getQuickPicks();
            const pickTexts = await Promise.all(picks.map(p => p.getText()));

            // Verify our commands are registered
            expect(pickTexts.some(text => text.includes('Compile Dashboard'))).to.be.true;
            expect(pickTexts.some(text => text.includes('Preview Dashboard'))).to.be.true;
            expect(pickTexts.some(text => text.includes('Export Dashboard'))).to.be.true;
            expect(pickTexts.some(text => text.includes('Edit Dashboard Layout'))).to.be.true;
        } finally {
            // Always cancel the command palette, even if assertions fail
            try {
                await inputBox.cancel();
            } catch {
                // Ignore errors during cleanup
            }
            // Double-check with ESC key
            try {
                const actions = driver.actions();
                await actions.sendKeys('\uE00C').perform();
                await driver.sleep(500);
            } catch {
                // Ignore
            }
        }
    });

    after(async () => {
        // Clean up: close all editors
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');
    });
});
