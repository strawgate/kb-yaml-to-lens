import * as vscode from 'vscode';
import { DashboardCompiler } from './compiler';
import { PreviewPanel } from './previewPanel';
import { setupFileWatcher } from './fileWatcher';

let compiler: DashboardCompiler;
let previewPanel: PreviewPanel;

/**
 * Validates that the active editor is a YAML file and returns its path.
 * Shows error messages if validation fails.
 * @returns The file path if valid, undefined otherwise
 */
function getActiveYamlFile(): string | undefined {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor');
        return undefined;
    }

    const fileName = editor.document.fileName;
    if (!fileName.endsWith('.yaml') && !fileName.endsWith('.yml')) {
        vscode.window.showErrorMessage('Active file is not a YAML file');
        return undefined;
    }

    return fileName;
}

export function activate(context: vscode.ExtensionContext) {
    console.log('YAML Dashboard Compiler extension is now active');

    compiler = new DashboardCompiler(context);
    previewPanel = new PreviewPanel(compiler);

    // Setup file watching for auto-compile
    const fileWatcherDisposables = setupFileWatcher(compiler, previewPanel);
    context.subscriptions.push(...fileWatcherDisposables);

    // Register compile command
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.compile', async () => {
            const filePath = getActiveYamlFile();
            if (!filePath) {
                return;
            }

            try {
                await vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: 'Compiling dashboard...'
                }, async () => {
                    await compiler.compile(filePath);
                    vscode.window.showInformationMessage('Dashboard compiled successfully');
                });
            } catch (error) {
                vscode.window.showErrorMessage(`Compilation failed: ${error instanceof Error ? error.message : String(error)}`);
            }
        })
    );

    // Register preview command
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.preview', async () => {
            const filePath = getActiveYamlFile();
            if (!filePath) {
                return;
            }

            await previewPanel.show(filePath);
        })
    );

    // Register export command
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.export', async () => {
            const filePath = getActiveYamlFile();
            if (!filePath) {
                return;
            }

            try {
                const result = await compiler.compile(filePath);
                const ndjson = JSON.stringify(result);
                await vscode.env.clipboard.writeText(ndjson);
                vscode.window.showInformationMessage('NDJSON copied to clipboard! Import in Kibana: Stack Management → Saved Objects → Import');
            } catch (error) {
                vscode.window.showErrorMessage(`Export failed: ${error instanceof Error ? error.message : String(error)}`);
            }
        })
    );
}

export function deactivate() {
    if (compiler) {
        compiler.dispose();
    }
}
