import * as vscode from 'vscode';
import { DashboardCompilerLSP } from './compiler';
import { PreviewPanel } from './previewPanel';
import { GridEditorPanel } from './gridEditorPanel';
import { setupFileWatcher } from './fileWatcher';
import { ConfigService } from './configService';
import * as fs from 'fs';
import { TextDecoder } from 'util';

let compiler: DashboardCompilerLSP;
let previewPanel: PreviewPanel;
let gridEditorPanel: GridEditorPanel;
let configService: ConfigService;
let uploadResultsChannel: vscode.OutputChannel | undefined;

/**
 * Checks if a YAML document contains a 'dashboards' root key.
 * Uses VS Code's TextDocument API when available to access in-memory content,
 * which works with both saved and unsaved changes.
 *
 * Following the pattern from vscode-kubernetes-tools extension:
 * - First try to find the document in VS Code's open documents (fast, in-memory)
 * - This works with unsaved changes and is more efficient than disk reads
 *
 * @param uri URI of the YAML file
 * @returns true if the file has a 'dashboards' root key, false otherwise
 */
function hasDashboardsKey(uri: string): boolean {
    try {
        const parsedUri = vscode.Uri.parse(uri);

        // Try to find the document in already opened/cached documents
        // This is synchronous and efficient - uses VS Code's existing document cache
        const document = vscode.workspace.textDocuments.find(
            doc => doc.uri.toString() === uri
        );

        let content: string;
        if (document) {
            // Document is already open - use in-memory content
            // This works with unsaved changes!
            content = document.getText();
        } else {
            // Document not open - need to read from disk
            // Note: This is a fallback. In practice, the YAML extension will have
            // opened the document before calling this contributor.
            content = fs.readFileSync(parsedUri.fsPath, 'utf-8');
        }

        // Check for 'dashboards:' at root level (start of line, no indentation)
        // This regex matches 'dashboards:' only when it appears at column 0 (no leading spaces/tabs)
        // The /m flag enables multiline mode so ^ matches the start of any line
        return /^dashboards\s*:/m.test(content);
    } catch (error) {
        // If we can't access the document, don't apply the schema
        return false;
    }
}

/**
 * Asynchronous version of hasDashboardsKey to prevent blocking the event loop.
 *
 * @param uri URI of the YAML file
 * @returns Promise resolving to true if the file has a 'dashboards' root key
 */
async function hasDashboardsKeyAsync(uri: vscode.Uri): Promise<boolean> {
    try {
        // Try to find the document in already opened/cached documents first
        const document = vscode.workspace.textDocuments.find(
            doc => doc.uri.toString() === uri.toString()
        );

        let content: string;
        if (document) {
            content = document.getText();
        } else {
            // Read asynchronously using VS Code API for virtual filesystem support
            const bytes = await vscode.workspace.fs.readFile(uri);
            content = new TextDecoder().decode(bytes);
        }

        return /^dashboards\s*:/m.test(content);
    } catch (error) {
        return false;
    }
}

/**
 * Process items in batches with bounded concurrency to prevent resource exhaustion.
 * This is particularly useful for large workspaces where processing all files
 * simultaneously could overwhelm system resources.
 *
 * @param items Array of items to process
 * @param batchSize Number of items to process concurrently (default: 20)
 * @param fn Async function to apply to each item
 * @returns Promise resolving to array of results in the same order as input items
 */
async function batchProcess<T, R>(
    items: T[],
    batchSize: number,
    fn: (item: T) => Promise<R>
): Promise<R[]> {
    const results: R[] = [];
    for (let i = 0; i < items.length; i += batchSize) {
        const batch = items.slice(i, i + batchSize);
        const batchResults = await Promise.all(batch.map(fn));
        results.push(...batchResults);
    }
    return results;
}

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

/**
 * Factory function to create dashboard commands with standard file/dashboard selection.
 * Reduces boilerplate by handling the common pattern of:
 * 1. Getting active YAML file
 * 2. Selecting dashboard
 * 3. Executing action
 *
 * @param action The action to execute with the file path and dashboard index
 * @returns A VS Code command handler
 */
function createDashboardCommand(action: (filePath: string, dashboardIndex: number) => Promise<void>): () => Promise<void> {
    return async () => {
        const filePath = getActiveYamlFile();
        if (!filePath) {
            return;
        }

        const dashboardIndex = await selectDashboard(filePath);
        if (dashboardIndex === undefined) {
            return;
        }

        await action(filePath, dashboardIndex);
    };
}

interface KibanaConfig {
    kibanaUrl: string;
    username: string;
    password: string;
    apiKey: string;
    sslVerify: boolean;
}

async function ensureKibanaConfig(configService: ConfigService): Promise<KibanaConfig | undefined> {
    let kibanaUrl = configService.getKibanaUrl();
    let username = await configService.getKibanaUsername();
    let password = await configService.getKibanaPassword();
    let apiKey = await configService.getKibanaApiKey();
    const sslVerify = configService.getKibanaSslVerify();

    if (!kibanaUrl || kibanaUrl === 'http://localhost:5601') {
        const promptedUrl = await vscode.window.showInputBox({
            prompt: 'Enter Kibana URL',
            placeHolder: 'https://your-kibana-instance.com',
            value: kibanaUrl,
            ignoreFocusOut: true,
            validateInput: (value) => {
                if (!value) {
                    return 'Kibana URL is required';
                }
                if (!value.startsWith('http://') && !value.startsWith('https://')) {
                    return 'URL must start with http:// or https://';
                }
                return undefined;
            }
        });

        if (!promptedUrl) {
            return undefined;
        }

        kibanaUrl = promptedUrl;
        await vscode.workspace.getConfiguration('yamlDashboard').update('kibana.url', kibanaUrl, vscode.ConfigurationTarget.Global);
    }

    if (!apiKey && (!username || !password)) {
        const authMethod = await vscode.window.showQuickPick(
            [
                { label: 'API Key (Recommended)', value: 'apiKey' },
                { label: 'Username/Password', value: 'basic' }
            ],
            {
                placeHolder: 'Select authentication method',
                ignoreFocusOut: true
            }
        );

        if (!authMethod) {
            return undefined;
        }

        if (authMethod.value === 'apiKey') {
            const promptedApiKey = await vscode.window.showInputBox({
                prompt: 'Enter Kibana API Key',
                placeHolder: 'Base64-encoded API key',
                password: true,
                ignoreFocusOut: true,
                validateInput: (value) => {
                    if (!value) {
                        return 'API Key is required';
                    }
                    return undefined;
                }
            });

            if (!promptedApiKey) {
                return undefined;
            }

            apiKey = promptedApiKey;
            await configService.setKibanaApiKey(apiKey);
        } else {
            const promptedUsername = await vscode.window.showInputBox({
                prompt: 'Enter Kibana username',
                placeHolder: 'elastic',
                ignoreFocusOut: true,
                validateInput: (value) => {
                    if (!value) {
                        return 'Username is required';
                    }
                    return undefined;
                }
            });

            if (!promptedUsername) {
                return undefined;
            }

            const promptedPassword = await vscode.window.showInputBox({
                prompt: 'Enter Kibana password',
                placeHolder: 'Password',
                password: true,
                ignoreFocusOut: true,
                validateInput: (value) => {
                    if (!value) {
                        return 'Password is required';
                    }
                    return undefined;
                }
            });

            if (!promptedPassword) {
                return undefined;
            }

            username = promptedUsername;
            password = promptedPassword;
            await configService.setKibanaUsername(username);
            await configService.setKibanaPassword(password);
        }
    }

    return {
        kibanaUrl,
        username: username || '',
        password: password || '',
        apiKey: apiKey || '',
        sslVerify
    };
}

/**
 * Register JSON schema with the YAML extension for auto-complete support.
 * This enables schema-based validation, hover documentation, and auto-complete
 * for dashboard YAML files.
 */
async function registerYamlSchema(): Promise<void> {
    // Check if YAML extension is available
    const yamlExtension = vscode.extensions.getExtension('redhat.vscode-yaml');
    if (!yamlExtension) {
        console.log('YAML extension not found - schema auto-complete disabled');
        return;
    }

    try {
        // Activate the YAML extension if not already active
        const yamlApi = await yamlExtension.activate();

        // Fetch schema from our LSP server
        const schemaResult = await compiler.getSchema();

        if (!schemaResult.success || !schemaResult.data) {
            console.error('Failed to get schema from LSP server:', schemaResult.error);
            return;
        }

        const schemaJSON = JSON.stringify(schemaResult.data);

        // Register the schema contributor
        // The contributor provides schemas for matching URIs
        yamlApi.registerContributor(
            'kb-yaml-to-lens',
            (uri: string) => {
                // Only apply schema to YAML files that contain a 'dashboards' root key
                // This prevents applying dashboard schema to other YAML files (CI configs, etc.)
                if (uri.endsWith('.yaml') || uri.endsWith('.yml')) {
                    if (hasDashboardsKey(uri)) {
                        return 'kb-yaml-to-lens://schema/dashboard';
                    }
                }
                return undefined;
            },
            (uri: string) => {
                // Return the schema content for our custom URI
                if (uri === 'kb-yaml-to-lens://schema/dashboard') {
                    return schemaJSON;
                }
                return undefined;
            }
        );

        console.log('YAML schema registered successfully');
    } catch (error) {
        console.error('Failed to register YAML schema:', error);
    }
}

export async function activate(context: vscode.ExtensionContext) {
    console.log('YAML Dashboard Compiler extension is now active');

    configService = new ConfigService(context);
    compiler = new DashboardCompilerLSP(context, configService);

    // Start the LSP server
    await compiler.start();

    // Register JSON schema with YAML extension for auto-complete
    await registerYamlSchema();

    previewPanel = new PreviewPanel(compiler);
    gridEditorPanel = new GridEditorPanel(context, configService);

    // Setup file watching for auto-compile
    const fileWatcherDisposables = setupFileWatcher(compiler, previewPanel, configService);
    context.subscriptions.push(...fileWatcherDisposables);

    // Register compile command
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.compile', createDashboardCommand(async (filePath, dashboardIndex) => {
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
        }))
    );

    // Register preview command
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.preview', createDashboardCommand(async (filePath, dashboardIndex) => {
            await previewPanel.show(filePath, dashboardIndex);
        }))
    );

    // Register export command
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.export', createDashboardCommand(async (filePath, dashboardIndex) => {
            try {
                const result = await compiler.compile(filePath, dashboardIndex);
                const ndjson = JSON.stringify(result);
                await vscode.env.clipboard.writeText(ndjson);
                vscode.window.showInformationMessage('NDJSON copied to clipboard! Import in Kibana: Stack Management → Saved Objects → Import');
            } catch (error) {
                vscode.window.showErrorMessage(`Export failed: ${error instanceof Error ? error.message : String(error)}`);
            }
        }))
    );

    // Register grid editor command
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.editLayout', createDashboardCommand(async (filePath, dashboardIndex) => {
            await gridEditorPanel.show(filePath, dashboardIndex);
        }))
    );

    // Register open in Kibana command
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.openInKibana', createDashboardCommand(async (filePath, dashboardIndex) => {
            try {
                const config = await ensureKibanaConfig(configService);
                if (!config) {
                    return;
                }

                const browserType = configService.getKibanaBrowserType();

                await vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: 'Opening dashboard in Kibana...',
                    cancellable: false
                }, async (progress) => {
                    progress.report({ message: 'Uploading to Kibana...' });

                    const { dashboardUrl, dashboardId } = await compiler.uploadToKibana(
                        filePath,
                        dashboardIndex,
                        config.kibanaUrl,
                        config.username,
                        config.password,
                        config.apiKey,
                        config.sslVerify
                    );

                    progress.report({ message: 'Opening browser...' });

                    const uri = vscode.Uri.parse(dashboardUrl);

                    if (browserType === 'simple') {
                        await vscode.commands.executeCommand('simpleBrowser.show', dashboardUrl);
                    } else {
                        await vscode.env.openExternal(uri);
                    }

                    vscode.window.showInformationMessage(
                        `Dashboard opened in Kibana (ID: ${dashboardId})`
                    );
                });
            } catch (error) {
                vscode.window.showErrorMessage(
                    `Failed to open in Kibana: ${error instanceof Error ? error.message : String(error)}`
                );
            }
        }))
    );

    // Register credential management commands
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.setKibanaUsername', async () => {
            const username = await vscode.window.showInputBox({
                prompt: 'Enter Kibana username',
                placeHolder: 'elastic',
                ignoreFocusOut: true
            });

            if (username !== undefined) {
                await configService.setKibanaUsername(username);
                vscode.window.showInformationMessage('Kibana username saved securely');
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.setKibanaPassword', async () => {
            const password = await vscode.window.showInputBox({
                prompt: 'Enter Kibana password',
                placeHolder: 'Password',
                password: true,
                ignoreFocusOut: true
            });

            if (password !== undefined) {
                await configService.setKibanaPassword(password);
                vscode.window.showInformationMessage('Kibana password saved securely');
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.setKibanaApiKey', async () => {
            const apiKey = await vscode.window.showInputBox({
                prompt: 'Enter Kibana API key',
                placeHolder: 'API key (recommended for security)',
                ignoreFocusOut: true
            });

            if (apiKey !== undefined) {
                await configService.setKibanaApiKey(apiKey);
                vscode.window.showInformationMessage('Kibana API key saved securely');
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.clearKibanaCredentials', async () => {
            const confirm = await vscode.window.showWarningMessage(
                'Clear all stored Kibana credentials?',
                { modal: true },
                'Clear'
            );

            if (confirm === 'Clear') {
                await configService.clearKibanaCredentials();
                vscode.window.showInformationMessage('Kibana credentials cleared');
            }
        })
    );

    // Register compile folder and upload to Kibana command
    context.subscriptions.push(
        vscode.commands.registerCommand('yamlDashboard.compileFolderAndUpload', async (uri: vscode.Uri) => {
            try {
                if (!uri || !uri.fsPath) {
                    vscode.window.showErrorMessage('No folder selected');
                    return;
                }

                const config = await ensureKibanaConfig(configService);
                if (!config) {
                    return;
                }

                const pattern = new vscode.RelativePattern(uri, '**/*.{yaml,yml}');
                const allFiles = await vscode.workspace.findFiles(pattern);

                // Use bounded-concurrency batching to prevent resource exhaustion in large workspaces
                const filterResults = await batchProcess(
                    allFiles,
                    20, // Process 20 files at a time
                    async (file) => {
                        const hasKey = await hasDashboardsKeyAsync(file);
                        return hasKey ? file : null;
                    }
                );
                const files = filterResults.filter((file): file is vscode.Uri => file !== null);

                if (files.length === 0) {
                    vscode.window.showInformationMessage('No YAML files with dashboards found in folder');
                    return;
                }

                // Track results
                interface UploadResult {
                    filePath: string;
                    success: boolean;
                    error?: string;
                    dashboardCount?: number;
                }
                const results: UploadResult[] = [];
                let wasCancelled = false;

                // Process files with progress
                await vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: `Uploading ${files.length} file(s) to Kibana...`,
                    cancellable: true
                }, async (progress, token) => {
                    for (let i = 0; i < files.length; i++) {
                        if (token.isCancellationRequested) {
                            vscode.window.showWarningMessage('Upload cancelled by user');
                            wasCancelled = true;
                            return;
                        }

                        const file = files[i];
                        const fileName = file.fsPath;
                        const displayName = vscode.workspace.asRelativePath(file);

                        progress.report({
                            message: `(${i + 1}/${files.length}) ${displayName}`,
                            increment: (100 / files.length)
                        });

                        try {
                            const dashboards = await compiler.getDashboards(fileName);

                            if (dashboards.length === 0) {
                                results.push({
                                    filePath: displayName,
                                    success: false,
                                    error: 'No dashboards found'
                                });
                                continue;
                            }

                            let uploadedCount = 0;
                            const errors: string[] = [];
                            for (const dashboard of dashboards) {
                                if (token.isCancellationRequested) {
                                    break;
                                }
                                try {
                                    await compiler.uploadToKibana(
                                        fileName,
                                        dashboard.index,
                                        config.kibanaUrl,
                                        config.username,
                                        config.password,
                                        config.apiKey,
                                        config.sslVerify
                                    );
                                    uploadedCount++;
                                } catch (error) {
                                    errors.push(error instanceof Error ? error.message : String(error));
                                }
                            }

                            results.push({
                                filePath: displayName,
                                success: uploadedCount > 0,
                                dashboardCount: uploadedCount,
                                error: errors.length > 0 ? `${uploadedCount}/${dashboards.length} uploaded; errors: ${errors.join('; ')}` : undefined
                            });
                        } catch (error) {
                            results.push({
                                filePath: displayName,
                                success: false,
                                error: error instanceof Error ? error.message : String(error)
                            });
                        }
                    }
                });

                if (wasCancelled) {
                    return;
                }

                // Show results summary
                const successCount = results.filter(r => r.success).length;
                const failureCount = results.filter(r => !r.success).length;
                const totalDashboards = results
                    .filter(r => r.success)
                    .reduce((sum, r) => sum + (r.dashboardCount || 0), 0);

                if (failureCount === 0) {
                    vscode.window.showInformationMessage(
                        `Successfully uploaded ${totalDashboards} dashboard(s) from ${successCount} file(s) to Kibana`
                    );
                } else {
                    const action = await vscode.window.showWarningMessage(
                        `Uploaded ${totalDashboards} dashboard(s) from ${successCount} file(s), ${failureCount} file(s) failed`,
                        'Show Details'
                    );

                    if (action === 'Show Details') {
                        if (!uploadResultsChannel) {
                            uploadResultsChannel = vscode.window.createOutputChannel('Kibana Upload Results');
                        }
                        const outputChannel = uploadResultsChannel;
                        outputChannel.clear();
                        outputChannel.appendLine('Kibana Upload Results');
                        outputChannel.appendLine('='.repeat(50));
                        outputChannel.appendLine('');

                        for (const result of results) {
                            if (result.success) {
                                outputChannel.appendLine(`✅ ${result.filePath} (${result.dashboardCount} dashboard(s))`);
                            } else {
                                outputChannel.appendLine(`❌ ${result.filePath}`);
                                outputChannel.appendLine(`   Error: ${result.error}`);
                            }
                        }

                        outputChannel.appendLine('');
                        outputChannel.appendLine('='.repeat(50));
                        outputChannel.appendLine(`Total: ${successCount} succeeded, ${failureCount} failed`);
                        outputChannel.show();
                    }
                }
            } catch (error) {
                vscode.window.showErrorMessage(
                    `Failed to upload folder: ${error instanceof Error ? error.message : String(error)}`
                );
            }
        })
    );
}

export async function deactivate(): Promise<void> {
    if (compiler) {
        await compiler.dispose();
    }
    if (uploadResultsChannel) {
        uploadResultsChannel.dispose();
    }
}
