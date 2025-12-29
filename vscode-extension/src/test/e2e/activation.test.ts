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

    it('should activate when opening a YAML file', async function() {
        this.timeout(30000);

        const workbench = new Workbench();

        // Open the test fixture file
        const fixturesPath = path.resolve(__dirname, '../../../test/fixtures/simple-dashboard.yaml');

        await workbench.executeCommand('workbench.action.files.openFile');

        // Type the file path in the input box
        const inputBox = await InputBox.create();
        await inputBox.setText(fixturesPath);
        await inputBox.confirm();

        // Wait a bit for the file to open
        await driver.sleep(2000);

        // Verify the editor is open
        const editorView = new EditorView();
        const titles = await editorView.getOpenEditorTitles();
        expect(titles).to.include('simple-dashboard.yaml');
    });

    it('should register all required commands', async function() {
        this.timeout(30000);

        const workbench = new Workbench();

        // Open command palette to search for our commands
        await workbench.executeCommand('workbench.action.showCommands');

        const inputBox = await InputBox.create();
        await inputBox.setText('YAML Dashboard');
        await driver.sleep(1000);

        const picks = await inputBox.getQuickPicks();
        const pickTexts = await Promise.all(picks.map(p => p.getText()));

        // Verify our commands are registered
        expect(pickTexts.some(text => text.includes('Compile Dashboard'))).to.be.true;
        expect(pickTexts.some(text => text.includes('Preview Dashboard'))).to.be.true;
        expect(pickTexts.some(text => text.includes('Export Dashboard'))).to.be.true;
        expect(pickTexts.some(text => text.includes('Edit Dashboard Layout'))).to.be.true;

        // Cancel the command palette
        await inputBox.cancel();
    });

    after(async () => {
        // Clean up: close all editors
        const workbench = new Workbench();
        await workbench.executeCommand('workbench.action.closeAllEditors');
    });
});
