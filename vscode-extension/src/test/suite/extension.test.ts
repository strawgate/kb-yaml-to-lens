import * as assert from 'assert';
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

suite('Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');

    test('Debug Workspace', async () => {
        console.log('Workspace folders:', vscode.workspace.workspaceFolders);
        if (vscode.workspace.workspaceFolders) {
            vscode.workspace.workspaceFolders.forEach(folder => {
                console.log('Folder:', folder.uri.fsPath);
            });
        }
    });

    test('Extension should be present', () => {
        const extension = vscode.extensions.getExtension('strawgate.yaml-dashboard-compiler');
        assert.ok(extension, 'Extension should be present');
    });

    test('Extension should activate', async () => {
        const extension = vscode.extensions.getExtension('strawgate.yaml-dashboard-compiler');
        assert.ok(extension);

        // Find the .venv path relative to this test file or the repo root
        // We are in /app/vscode-extension/out/test/suite/extension.test.js
        // Repo root is /app

        // Try to find .venv in typical locations
        const potentialPaths = [
            path.resolve(__dirname, '../../../../.venv/bin/python'), // From compiled test file to repo root
            path.resolve('/app/.venv/bin/python') // Absolute path in this environment
        ];

        let pythonPath = potentialPaths.find(p => fs.existsSync(p));

        if (!pythonPath) {
             console.log('Could not find .venv/bin/python in:', potentialPaths);
             // Fallback to system python if venv missing (though we expect it to be there)
             pythonPath = 'python';
        } else {
            console.log('Found python at:', pythonPath);
        }

        const config = vscode.workspace.getConfiguration('yamlDashboard');
        // Update global config if workspace is not available, or workspace config if it is
        const target = vscode.workspace.workspaceFolders ? vscode.ConfigurationTarget.Workspace : vscode.ConfigurationTarget.Global;
        await config.update('pythonPath', pythonPath, target);

        // Wait for activation
        if (!extension.isActive) {
            await extension.activate();
        }
        assert.ok(extension.isActive);
    });

    test('Should register commands', async () => {
        const extension = vscode.extensions.getExtension('strawgate.yaml-dashboard-compiler');
        if (!extension?.isActive) {
            await extension?.activate();
        }

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
        // This test specifically verifies the getDashboards custom request works
        // which was failing with AttributeError: 'Object' object has no attribute 'get'
        const extension = vscode.extensions.getExtension('strawgate.yaml-dashboard-compiler');
        assert.ok(extension);

        if (!extension.isActive) {
            await extension.activate();
        }

        const fixturePath = path.resolve(__dirname, '../../../src/test/fixtures/test.yaml');
        if (!fs.existsSync(fixturePath)) {
            const fallbackPath = path.resolve(__dirname, '../fixtures/test.yaml');
            if (!fs.existsSync(fallbackPath)) {
                assert.fail(`Fixture not found at ${fixturePath} or ${fallbackPath}`);
            }
        }

        // Get the compiler from the extension's exports (if available)
        // For now, we'll test it indirectly through the compile command which calls getDashboards
        const uri = vscode.Uri.file(fixturePath);
        const doc = await vscode.workspace.openTextDocument(uri);
        await vscode.window.showTextDocument(doc);

        // Give the LSP server a moment to initialize
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Execute compile command - this internally calls getDashboards()
        // and will fail if the AttributeError occurs
        try {
            await vscode.commands.executeCommand('yamlDashboard.compile');
        } catch (error) {
            assert.fail(`getDashboards failed: ${error}`);
        }
    });

    test('Should open YAML file and compile', async () => {
        // Construct path to fixture relative to this file
        // The fixture is in src/test/fixtures/test.yaml
        // compiled test file is in out/test/suite/extension.test.js
        // so we need ../../../src/test/fixtures/test.yaml relative to __dirname (out/test/suite)

        const fixturePath = path.resolve(__dirname, '../../../src/test/fixtures/test.yaml');

        if (!fs.existsSync(fixturePath)) {
            // Check potential fallback location
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

            // Give it a moment to stabilize
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Execute the compile command
            // Since there is only one dashboard in the file, it should proceed without prompting
            await vscode.commands.executeCommand('yamlDashboard.compile');

            // If we reached here without error, it's likely successful.

        } catch (error) {
             assert.fail(`Test failed: ${error}`);
        }
    });
});
