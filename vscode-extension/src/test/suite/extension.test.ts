import * as assert from 'assert';
import * as path from 'path';
import * as vscode from 'vscode';

const EXTENSION_ID = 'strawgate.yaml-dashboard-compiler';
const FIXTURES_PATH = path.join(__dirname, '..', '..', '..', 'src', 'test', 'fixtures');
const LSP_STARTUP_DELAY_MS = 3000;

suite('Extension E2E Tests', () => {
    let extension: vscode.Extension<unknown> | undefined;

    suiteSetup(async function () {
        this.timeout(30000);

        // Open a YAML file to trigger extension activation
        const yamlFile = path.join(FIXTURES_PATH, 'simple-dashboard.yaml');
        const document = await vscode.workspace.openTextDocument(yamlFile);
        await vscode.window.showTextDocument(document);

        // Wait for extension to activate
        extension = vscode.extensions.getExtension(EXTENSION_ID);
        if (extension && !extension.isActive) {
            await extension.activate();
        }

        // Give the LSP server time to start
        await new Promise(resolve => setTimeout(resolve, LSP_STARTUP_DELAY_MS));
    });

    test('Extension should be present', () => {
        assert.ok(extension, 'Extension should be installed');
    });

    test('Extension should activate on YAML files', async function () {
        this.timeout(10000);
        assert.ok(extension?.isActive, 'Extension should be active');
    });

    test('Commands should be registered', async () => {
        const commands = await vscode.commands.getCommands(true);

        const expectedCommands = [
            'yamlDashboard.compile',
            'yamlDashboard.preview',
            'yamlDashboard.export',
            'yamlDashboard.editLayout'
        ];

        for (const cmd of expectedCommands) {
            assert.ok(
                commands.includes(cmd),
                `Command ${cmd} should be registered`
            );
        }
    });

    test('Should open simple dashboard YAML file', async function () {
        this.timeout(10000);

        const yamlFile = path.join(FIXTURES_PATH, 'simple-dashboard.yaml');
        const document = await vscode.workspace.openTextDocument(yamlFile);
        await vscode.window.showTextDocument(document);

        assert.strictEqual(document.languageId, 'yaml');
        assert.ok(document.getText().includes('Test Dashboard'));
    });

    test('Should open multi-dashboard YAML file', async function () {
        this.timeout(10000);

        const yamlFile = path.join(FIXTURES_PATH, 'multi-dashboard.yaml');
        const document = await vscode.workspace.openTextDocument(yamlFile);
        await vscode.window.showTextDocument(document);

        assert.strictEqual(document.languageId, 'yaml');
        assert.ok(document.getText().includes('First Dashboard'));
        assert.ok(document.getText().includes('Second Dashboard'));
    });

    test('Should handle invalid YAML file', async function () {
        this.timeout(10000);

        const yamlFile = path.join(FIXTURES_PATH, 'invalid.yaml');
        const document = await vscode.workspace.openTextDocument(yamlFile);
        await vscode.window.showTextDocument(document);

        assert.strictEqual(document.languageId, 'yaml');
        assert.ok(document.getText().includes('Missing Grid'));
    });
});
