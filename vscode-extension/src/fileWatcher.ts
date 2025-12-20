import * as vscode from 'vscode';
import { DashboardCompiler } from './compiler';
import { PreviewPanel } from './previewPanel';

export function setupFileWatcher(compiler: DashboardCompiler, previewPanel: PreviewPanel): vscode.Disposable[] {
    // Watch for saves on YAML files
    const saveWatcher = vscode.workspace.onDidSaveTextDocument(async (document) => {
        if (!document.fileName.endsWith('.yaml') && !document.fileName.endsWith('.yml')) {
            return;
        }

        const config = vscode.workspace.getConfiguration('yamlDashboard');
        const compileOnSave = config.get<boolean>('compileOnSave', true);

        if (compileOnSave) {
            try {
                await vscode.window.withProgress({
                    location: vscode.ProgressLocation.Window,
                    title: 'Compiling dashboard...'
                }, async () => {
                    // Preview panel's updatePreview will call compile internally,
                    // so we don't need to compile twice
                    await previewPanel.updatePreview(document.fileName);
                });

                // Show subtle success message in status bar
                vscode.window.setStatusBarMessage('$(check) Dashboard compiled', 3000);
            } catch (error) {
                vscode.window.showErrorMessage(`Compilation failed: ${error instanceof Error ? error.message : String(error)}`);
            }
        }
    });

    // Also watch for general file system changes - support both .yaml and .yml
    const fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.{yaml,yml}');

    fileWatcher.onDidChange(async (uri) => {
        const config = vscode.workspace.getConfiguration('yamlDashboard');
        const compileOnSave = config.get<boolean>('compileOnSave', true);

        if (compileOnSave) {
            // Update preview if it's open
            await previewPanel.updatePreview(uri.fsPath);
        }
    });

    return [saveWatcher, fileWatcher];
}
