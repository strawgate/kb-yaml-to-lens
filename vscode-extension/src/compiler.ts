/**
 * LSP-based Dashboard Compiler using vscode-languageclient
 *
 * This implementation uses the Language Server Protocol to provide
 * dashboard compilation services to the VS Code extension.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
} from 'vscode-languageclient/node';

// Interface for the compiled dashboard result
export type CompiledDashboard = unknown;

export interface DashboardInfo {
    index: number;
    title: string;
    description: string;
}

interface CompileResult {
    success: boolean;
    data?: CompiledDashboard;
    error?: string;
}

interface DashboardListResult {
    success: boolean;
    data?: DashboardInfo[];
    error?: string;
}

export class DashboardCompilerLSP {
    private client: LanguageClient | null = null;
    private outputChannel: vscode.OutputChannel;

    constructor(private context: vscode.ExtensionContext) {
        this.outputChannel = vscode.window.createOutputChannel('Dashboard Compiler LSP');
    }

    /**
     * Resolve the Python path to use for the LSP server.
     * Checks in order:
     * 1. Configured pythonPath setting (resolves relative paths to workspace)
     * 2. Workspace .venv/bin/python (or Scripts/python.exe on Windows)
     * 3. Falls back to 'python' system command
     */
    private resolvePythonPath(): string {
        const config = vscode.workspace.getConfiguration('yamlDashboard');
        const configuredPath = config.get<string>('pythonPath', 'python');
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const workspaceRoot = workspaceFolders?.[0]?.uri.fsPath;

        // If user explicitly configured a path (not default), resolve and use it
        if (configuredPath !== 'python') {
            let resolvedPath = configuredPath;

            // Resolve relative paths against workspace root
            if (workspaceRoot && !path.isAbsolute(configuredPath)) {
                resolvedPath = path.join(workspaceRoot, configuredPath);
            }

            if (fs.existsSync(resolvedPath)) {
                this.outputChannel.appendLine(`Using configured Python path: ${resolvedPath}`);
                return resolvedPath;
            }

            // Configured path doesn't exist, warn and fall through to auto-detection
            this.outputChannel.appendLine(`Warning: Configured Python path not found: ${resolvedPath}`);
        }

        // Try to auto-detect workspace .venv
        if (workspaceRoot) {
            const isWindows = process.platform === 'win32';
            const venvPython = isWindows
                ? path.join(workspaceRoot, '.venv', 'Scripts', 'python.exe')
                : path.join(workspaceRoot, '.venv', 'bin', 'python');

            if (fs.existsSync(venvPython)) {
                this.outputChannel.appendLine(`Auto-detected workspace venv: ${venvPython}`);
                return venvPython;
            }
        }

        this.outputChannel.appendLine(`Using system Python: python`);
        return 'python';
    }

    async start(): Promise<void> {
        if (this.client) {
            return; // Already started
        }

        const pythonPath = this.resolvePythonPath();

        // Path to the LSP server script
        const extensionPath = this.context.extensionPath;
        const serverScript = path.join(extensionPath, 'python', 'compile_server.py');

        // Server options - how to start the Python LSP server
        const serverOptions: ServerOptions = {
            command: pythonPath,
            args: [serverScript],
            options: {
                cwd: path.join(extensionPath, '..'), // Set cwd to repo root
            },
        };

        // Client options - what files the LSP server should watch
        const clientOptions: LanguageClientOptions = {
            // Register the server for YAML files
            documentSelector: [{ scheme: 'file', language: 'yaml' }],

            // Synchronize file changes - notify server when YAML files change
            synchronize: {
                fileEvents: vscode.workspace.createFileSystemWatcher('**/*.{yaml,yml}'),
            },

            // Use our output channel for logging
            outputChannel: this.outputChannel,
        };

        // Create the language client
        this.client = new LanguageClient(
            'dashboardCompiler',
            'Dashboard Compiler',
            serverOptions,
            clientOptions
        );

        // Start the client (this will also start the server)
        await this.client.start();

        // Register notification handler for file changes
        this.client.onNotification('dashboard/fileChanged', (params: { uri: string }) => {
            this.outputChannel.appendLine(`Dashboard file changed: ${params.uri}`);
        });
    }

    /**
     * Compile a dashboard from a YAML file.
     *
     * @param filePath Path to the YAML file
     * @param dashboardIndex Index of the dashboard to compile (default: 0)
     * @returns Compiled dashboard object
     */
    async compile(filePath: string, dashboardIndex: number = 0): Promise<CompiledDashboard> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        const result = await this.client.sendRequest<CompileResult>(
            'dashboard/compile',
            // eslint-disable-next-line @typescript-eslint/naming-convention
            { path: filePath, dashboard_index: dashboardIndex }
        );

        if (!result.success) {
            throw new Error(result.error || 'Compilation failed');
        }

        return result.data as CompiledDashboard;
    }

    /**
     * Get list of dashboards from a YAML file.
     *
     * @param filePath Path to the YAML file
     * @returns Array of dashboard information objects
     */
    async getDashboards(filePath: string): Promise<DashboardInfo[]> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        const result = await this.client.sendRequest<DashboardListResult>(
            'dashboard/getDashboards',
            { path: filePath }
        );

        if (!result.success) {
            throw new Error(result.error || 'Failed to get dashboards');
        }

        return result.data || [];
    }

    async dispose(): Promise<void> {
        if (this.client) {
            await this.client.stop();
            this.client = null;
        }
        this.outputChannel.dispose();
    }
}
