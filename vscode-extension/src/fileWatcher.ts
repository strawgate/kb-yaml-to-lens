import * as vscode from 'vscode';
import { DashboardCompilerLSP } from './compiler';
import { PreviewPanel } from './previewPanel';
import { ConfigService } from './configService';

export function setupFileWatcher(
    compiler: DashboardCompilerLSP,
    previewPanel: PreviewPanel,
    configService: ConfigService
): vscode.Disposable[] {
    // Watch for saves on YAML files
    const saveWatcher = vscode.workspace.onDidSaveTextDocument(async (document) => {
        if (!document.fileName.endsWith('.yaml') && !document.fileName.endsWith('.yml')) {
            return;
        }

        const compileOnSave = configService.getCompileOnSave();
        const uploadOnSave = configService.getKibanaUploadOnSave();

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

        // Upload to Kibana if enabled
        if (uploadOnSave) {
            try {
                // Get Kibana configuration
                const kibanaUrl = configService.getKibanaUrl();
                const username = await configService.getKibanaUsername();
                const password = await configService.getKibanaPassword();
                const apiKey = await configService.getKibanaApiKey();
                const sslVerify = configService.getKibanaSslVerify();

                // Skip if no URL or credentials configured
                if (!kibanaUrl || kibanaUrl.includes('localhost') || kibanaUrl.includes('127.0.0.1')) {
                    return;
                }
                // Need either API key OR both username and password
                const hasApiKey = apiKey && apiKey.length > 0;
                const hasBasicAuth = username && username.length > 0 && password && password.length > 0;
                if (!hasApiKey && !hasBasicAuth) {
                    return;
                }

                await vscode.window.withProgress({
                    location: vscode.ProgressLocation.Window,
                    title: 'Uploading to Kibana...'
                }, async () => {
                    const { dashboardId } = await compiler.uploadToKibana(
                        document.fileName,
                        0, // Default to first dashboard
                        kibanaUrl,
                        username,
                        password,
                        apiKey,
                        sslVerify
                    );

                    // Show subtle success message in status bar
                    vscode.window.setStatusBarMessage(`$(cloud-upload) Uploaded to Kibana (ID: ${dashboardId})`, 5000);
                });
            } catch (error) {
                // Silent failure - just show in status bar, don't interrupt workflow
                vscode.window.setStatusBarMessage(`$(error) Kibana upload failed: ${error instanceof Error ? error.message : String(error)}`, 5000);
            }
        }
    });

    // Also watch for general file system changes - support both .yaml and .yml
    const fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.{yaml,yml}');

    fileWatcher.onDidChange(async (uri) => {
        const compileOnSave = configService.getCompileOnSave();

        if (compileOnSave) {
            // Update preview if it's open
            await previewPanel.updatePreview(uri.fsPath);
        }
    });

    return [saveWatcher, fileWatcher];
}
