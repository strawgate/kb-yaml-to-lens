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
        workspaceRoot && path.join(workspaceRoot, 'packages/kb-dashboard-cli/.venv/bin/python'),
        path.join(process.cwd(), 'packages/kb-dashboard-cli/.venv/bin/python'),
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

/**
 * Resolve fixture path, checking both source and compiled output locations.
 */
function resolveFixturePath(relativePath: string): string {
    const fixturePath = path.resolve(__dirname, `../../../src/test/fixtures/${relativePath}`);
    const fallbackPath = path.resolve(__dirname, `../fixtures/${relativePath}`);

    if (fs.existsSync(fixturePath)) {
        return fixturePath;
    }
    if (fs.existsSync(fallbackPath)) {
        return fallbackPath;
    }
    assert.fail(`Fixture not found at ${fixturePath} or ${fallbackPath}`);
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

    test('Workspace folders should be configured', async () => {
        assert.ok(vscode.workspace.workspaceFolders, 'Workspace folders should be defined');
        assert.ok(vscode.workspace.workspaceFolders.length > 0, 'At least one workspace folder should exist');
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

    test('Should open YAML file and verify it is recognized as YAML', async () => {
        const actualPath = resolveFixturePath('test.yaml');

        const uri = vscode.Uri.file(actualPath);
        const doc = await vscode.workspace.openTextDocument(uri);
        await vscode.window.showTextDocument(doc);

        assert.strictEqual(doc.languageId, 'yaml', 'Document should be recognized as YAML');
        const text = doc.getText();
        assert.ok(text.length > 0, 'Document should have content');
        assert.match(text, /^\s*dashboards:/m, 'Document should contain dashboard definition');
    });

    test('Should compile YAML file without errors', async () => {
        const actualPath = resolveFixturePath('test.yaml');

        const uri = vscode.Uri.file(actualPath);
        const doc = await vscode.workspace.openTextDocument(uri);
        await vscode.window.showTextDocument(doc);

        // Extension initialized via suiteSetup; command throws on failure
        await vscode.commands.executeCommand('yamlDashboard.compile');

        // Verify no diagnostic errors for the compiled file
        const diagnostics = vscode.languages.getDiagnostics(uri);
        const errors = diagnostics.filter(d => d.severity === vscode.DiagnosticSeverity.Error);
        assert.strictEqual(errors.length, 0, `Expected no errors but found: ${errors.map(e => e.message).join(', ')}`);
    });
});
