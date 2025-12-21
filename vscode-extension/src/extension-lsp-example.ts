/**
 * Example of how to integrate the LSP-based compiler into the extension.
 *
 * This shows how extension.ts would be modified to use the LSP implementation.
 */

import * as vscode from 'vscode';
import { DashboardCompilerLSP } from './compiler-lsp';

export async function activate(context: vscode.ExtensionContext) {
    console.log('YAML Dashboard Compiler (LSP) is now active');

    // Create the LSP-based compiler
    const compiler = new DashboardCompilerLSP(context);

    // Start the LSP server
    await compiler.start();

    // Register the compile command
    const compileCommand = vscode.commands.registerCommand(
        'yamlDashboard.compile',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor');
                return;
            }

            const filePath = editor.document.uri.fsPath;

            try {
                // Check if file has multiple dashboards
                const dashboards = await compiler.getDashboards(filePath);

                let dashboardIndex = 0;
                if (dashboards.length > 1) {
                    // Let user pick which dashboard to compile
                    const items = dashboards.map(d => ({
                        label: d.title,
                        description: d.description,
                        index: d.index
                    }));

                    const selected = await vscode.window.showQuickPick(items, {
                        placeHolder: 'Select a dashboard to compile'
                    });

                    if (!selected) {
                        return; // User cancelled
                    }

                    dashboardIndex = selected.index;
                }

                // Show progress while compiling
                await vscode.window.withProgress(
                    {
                        location: vscode.ProgressLocation.Notification,
                        title: 'Compiling dashboard...',
                        cancellable: false
                    },
                    async () => {
                        const result = await compiler.compile(filePath, dashboardIndex);

                        // Show success message
                        vscode.window.showInformationMessage('Dashboard compiled successfully!');

                        // Could do something with the result here
                        // e.g., show preview, save to file, upload to Kibana, etc.
                        console.log('Compiled dashboard:', result);
                    }
                );
            } catch (error) {
                vscode.window.showErrorMessage(
                    `Compilation failed: ${error instanceof Error ? error.message : String(error)}`
                );
            }
        }
    );

    // Register dispose handler
    context.subscriptions.push(
        compileCommand,
        {
            dispose: () => compiler.dispose()
        }
    );

    // Example: Auto-compile on save (if enabled in settings)
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(async (document) => {
            const config = vscode.workspace.getConfiguration('yamlDashboard');
            const compileOnSave = config.get<boolean>('compileOnSave', false);

            if (compileOnSave && document.languageId === 'yaml') {
                // The LSP server will automatically receive a textDocument/didSave notification
                // You can trigger recompilation here if desired
                try {
                    const dashboards = await compiler.getDashboards(document.uri.fsPath);
                    if (dashboards.length > 0) {
                        // Auto-compile the first dashboard
                        await compiler.compile(document.uri.fsPath, 0);
                        vscode.window.showInformationMessage('Dashboard auto-compiled on save');
                    }
                } catch (error) {
                    console.error('Auto-compile failed:', error);
                }
            }
        })
    );
}

export function deactivate() {
    // Cleanup is handled by the dispose subscriptions
}

/**
 * Key differences from current extension.ts:
 *
 * 1. Compiler initialization:
 *    OLD: const compiler = new DashboardCompiler(context);
 *    NEW: const compiler = new DashboardCompilerLSP(context);
 *         await compiler.start();  // Async start required for LSP
 *
 * 2. Error handling:
 *    - LSP provides better error messages through structured error types
 *    - Server crashes are auto-handled by LanguageClient
 *
 * 3. File watching:
 *    - LSP automatically watches files specified in synchronize.fileEvents
 *    - Server receives textDocument/didSave automatically
 *    - Can react to server notifications via client.onNotification()
 *
 * 4. Progress reporting:
 *    - Could use LSP's built-in progress reporting (window/workDoneProgress)
 *    - Server can send progress updates during long compilations
 *
 * 5. Diagnostics (optional future feature):
 *    - Server can send diagnostics as user types
 *    - Errors/warnings show up as squiggly lines in editor
 *    - No extra code needed in extension.ts - LSP handles it
 */
