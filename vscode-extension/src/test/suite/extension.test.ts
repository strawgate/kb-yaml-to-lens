import * as assert from 'assert';
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

/**
 * Find Python interpreter with dashboard_compiler module.
 * Searches in order: workspace root, process.cwd(), fallback to python3
 */
function findPythonPath(): string {
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

    const candidates = [
        workspaceRoot && path.join(workspaceRoot, 'compiler/.venv/bin/python'),
        path.join(process.cwd(), 'compiler/.venv/bin/python'),
        'python3'
    ].filter((p): p is string => !!p);

    const found = candidates.find(p => {
        try {
            return fs.existsSync(p) || p === 'python3';
        } catch {
            return false;
        }
    }) || 'python3';

    console.log(`Using Python interpreter: ${found}`);
    return found;
}

suite('Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');

    // Configure Python path before all tests to ensure consistent extension state
    suiteSetup(async function() {
        // Increase timeout for extension activation
        this.timeout(10000);

        try {
            const pythonPath = findPythonPath();
            const config = vscode.workspace.getConfiguration('yamlDashboard');
            const target = vscode.workspace.workspaceFolders
                ? vscode.ConfigurationTarget.Workspace
                : vscode.ConfigurationTarget.Global;
            await config.update('pythonPath', pythonPath, target);

            // Ensure extension is activated with the correct config
            const extension = vscode.extensions.getExtension('strawgate.kb-dashboard-compiler');
            if (extension && !extension.isActive) {
                await extension.activate();
            }
        } catch (error) {
            throw new Error(`Test setup failed: ${error instanceof Error ? error.message : String(error)}`);
        }
    });

    test('Extension should be present', () => {
        const extension = vscode.extensions.getExtension('strawgate.kb-dashboard-compiler');
        assert.ok(extension, 'Extension should be present');
    });

    test('Extension should activate', async () => {
        const extension = vscode.extensions.getExtension('strawgate.kb-dashboard-compiler');
        assert.ok(extension);
        assert.ok(extension.isActive, 'Extension should be activated by before() hook');
    });

    test('Should register commands', async () => {
        const commands = await vscode.commands.getCommands(true);
        assert.ok(commands.includes('yamlDashboard.compile'), 'yamlDashboard.compile command missing');
        assert.ok(commands.includes('yamlDashboard.preview'), 'yamlDashboard.preview command missing');
        assert.ok(commands.includes('yamlDashboard.openInKibana'), 'yamlDashboard.openInKibana command missing');
        assert.ok(commands.includes('yamlDashboard.setKibanaUsername'), 'yamlDashboard.setKibanaUsername command missing');
        assert.ok(commands.includes('yamlDashboard.setKibanaPassword'), 'yamlDashboard.setKibanaPassword command missing');
        assert.ok(commands.includes('yamlDashboard.setKibanaApiKey'), 'yamlDashboard.setKibanaApiKey command missing');
        assert.ok(commands.includes('yamlDashboard.clearKibanaCredentials'), 'yamlDashboard.clearKibanaCredentials command missing');
    });

    test('Should get dashboards from YAML file', async () => {
        const fixturePath = path.resolve(__dirname, '../../../src/test/fixtures/test.yaml');
        if (!fs.existsSync(fixturePath)) {
            const fallbackPath = path.resolve(__dirname, '../fixtures/test.yaml');
            if (!fs.existsSync(fallbackPath)) {
                assert.fail(`Fixture not found at ${fixturePath} or ${fallbackPath}`);
            }
        }

        const uri = vscode.Uri.file(fixturePath);
        const doc = await vscode.workspace.openTextDocument(uri);
        await vscode.window.showTextDocument(doc);

        // Give the LSP server a moment to initialize
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Execute compile command - this internally calls getDashboards()
        try {
            await vscode.commands.executeCommand('yamlDashboard.compile');
        } catch (error) {
            assert.fail(`getDashboards failed: ${error}`);
        }
    });

    test('Should open YAML file and compile', async () => {
        const fixturePath = path.resolve(__dirname, '../../../src/test/fixtures/test.yaml');

        if (!fs.existsSync(fixturePath)) {
            const fallbackPath = path.resolve(__dirname, '../fixtures/test.yaml');
            if (!fs.existsSync(fallbackPath)) {
                assert.fail(`Fixture not found at ${fixturePath} or ${fallbackPath}`);
            }
        }

        const uri = vscode.Uri.file(fixturePath);

        try {
            const doc = await vscode.workspace.openTextDocument(uri);
            await vscode.window.showTextDocument(doc);
            assert.strictEqual(doc.languageId, 'yaml');

            // Give LSP server a moment to initialize
            await new Promise(resolve => setTimeout(resolve, 1000));

            await vscode.commands.executeCommand('yamlDashboard.compile');
        } catch (error) {
            assert.fail(`Test failed: ${error}`);
        }
    });
});
