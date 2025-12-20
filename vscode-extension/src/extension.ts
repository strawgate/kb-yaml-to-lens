import * as vscode from 'vscode';
import { DashboardCompiler } from './compiler';
import { PreviewPanel } from './previewPanel';
import { setupFileWatcher } from './fileWatcher';

let compiler: DashboardCompiler;
let previewPanel: PreviewPanel;

export function activate(context: vscode.ExtensionContext) {
    console.log('YAML Dashboard Compiler extension is now active');

    compiler = new DashboardCompiler(context);
    previewPanel = new PreviewPanel(compiler);

    // Setup file watching for auto-compile
    setupFileWatcher(compiler, previewPanel);

    // Register compile command
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.compile', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor');
                return;
            }

            if (!editor.document.fileName.endsWith('.yaml')) {
                vscode.window.showErrorMessage('Active file is not a YAML file');
                return;
            }

            try {
                await vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: 'Compiling dashboard...'
                }, async () => {
                    await compiler.compile(editor.document.fileName);
                    vscode.window.showInformationMessage('Dashboard compiled successfully');
                });
            } catch (error) {
                vscode.window.showErrorMessage(`Compilation failed: ${error}`);
            }
        })
    );

    // Register preview command
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.preview', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor');
                return;
            }

            if (!editor.document.fileName.endsWith('.yaml')) {
                vscode.window.showErrorMessage('Active file is not a YAML file');
                return;
            }

            await previewPanel.show(editor.document.fileName);
        })
    );

    // Register export command
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.export', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor');
                return;
            }

            if (!editor.document.fileName.endsWith('.yaml')) {
                vscode.window.showErrorMessage('Active file is not a YAML file');
                return;
            }

            try {
                const result = await compiler.compile(editor.document.fileName);
                const ndjson = JSON.stringify(result);
                await vscode.env.clipboard.writeText(ndjson);
                vscode.window.showInformationMessage('NDJSON copied to clipboard! Import in Kibana: Stack Management → Saved Objects → Import');
            } catch (error) {
                vscode.window.showErrorMessage(`Export failed: ${error}`);
            }
        })
    );
}

export function deactivate() {
    if (compiler) {
        compiler.dispose();
    }
}
