import * as vscode from 'vscode';
import { DashboardCompiler } from './compiler';
import { PreviewPanel } from './previewPanel';

export function setupFileWatcher(compiler: DashboardCompiler, previewPanel: PreviewPanel) {
    // Watch for saves on YAML files
    vscode.workspace.onDidSaveTextDocument(async (document) => {
        if (!document.fileName.endsWith('.yaml')) {
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
                    await compiler.compile(document.fileName);
                });

                // Update preview if it's open
                await previewPanel.updatePreview(document.fileName);

                // Show subtle success message in status bar
                vscode.window.setStatusBarMessage('$(check) Dashboard compiled', 3000);
            } catch (error) {
                vscode.window.showErrorMessage(`Compilation failed: ${error}`);
            }
        }
    });

    // Also watch for general file system changes
    const fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.yaml');

    fileWatcher.onDidChange(async (uri) => {
        const config = vscode.workspace.getConfiguration('yamlDashboard');
        const compileOnSave = config.get<boolean>('compileOnSave', true);

        if (compileOnSave) {
            // Update preview if it's open
            await previewPanel.updatePreview(uri.fsPath);
        }
    });

    return fileWatcher;
}
