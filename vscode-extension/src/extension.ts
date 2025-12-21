import * as vscode from 'vscode';
import { DashboardCompiler } from './compiler';
import { PreviewPanel } from './previewPanel';
import { GridEditorPanel } from './gridEditorPanel';
import { setupFileWatcher } from './fileWatcher';

let compiler: DashboardCompiler;
let previewPanel: PreviewPanel;
let gridEditorPanel: GridEditorPanel;

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

/**
 * Gets the dashboard index to use for the given file.
 * If the file contains multiple dashboards, prompts the user to select one.
 * @param filePath Path to the YAML file
 * @returns The dashboard index, or undefined if the user cancelled
 */
async function selectDashboard(filePath: string): Promise<number | undefined> {
    try {
        const dashboards = await compiler.getDashboards(filePath);

        if (dashboards.length === 0) {
            vscode.window.showErrorMessage('No dashboards found in file');
            return undefined;
        }

        if (dashboards.length === 1) {
            // Only one dashboard, use it directly
            return 0;
        }

        // Multiple dashboards, show quick pick
        const items = dashboards.map(d => ({
            label: d.title,
            description: d.description || `Dashboard ${d.index + 1}`,
            index: d.index
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select a dashboard to work with'
        });

        return selected?.index;
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to get dashboards: ${error instanceof Error ? error.message : String(error)}`);
        return undefined;
    }
}

export function activate(context: vscode.ExtensionContext) {
    console.log('YAML Dashboard Compiler extension is now active');

    compiler = new DashboardCompiler(context);
    previewPanel = new PreviewPanel(compiler);
    gridEditorPanel = new GridEditorPanel(context);

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

            const dashboardIndex = await selectDashboard(filePath);
            if (dashboardIndex === undefined) {
                return;
            }

            try {
                await vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: 'Compiling dashboard...'
                }, async () => {
                    await compiler.compile(filePath, dashboardIndex);
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

            const dashboardIndex = await selectDashboard(filePath);
            if (dashboardIndex === undefined) {
                return;
            }

            await previewPanel.show(filePath, dashboardIndex);
        })
    );

    // Register export command
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.export', async () => {
            const filePath = getActiveYamlFile();
            if (!filePath) {
                return;
            }

            const dashboardIndex = await selectDashboard(filePath);
            if (dashboardIndex === undefined) {
                return;
            }

            try {
                const result = await compiler.compile(filePath, dashboardIndex);
                const ndjson = JSON.stringify(result);
                await vscode.env.clipboard.writeText(ndjson);
                vscode.window.showInformationMessage('NDJSON copied to clipboard! Import in Kibana: Stack Management → Saved Objects → Import');
            } catch (error) {
                vscode.window.showErrorMessage(`Export failed: ${error instanceof Error ? error.message : String(error)}`);
            }
        })
    );

    // Register grid editor command
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.editLayout', async () => {
            const filePath = getActiveYamlFile();
            if (!filePath) {
                return;
            }

            const dashboardIndex = await selectDashboard(filePath);
            if (dashboardIndex === undefined) {
                return;
            }

            await gridEditorPanel.show(filePath, dashboardIndex);
        })
    );
}

export function deactivate() {
    if (compiler) {
        compiler.dispose();
    }
}
