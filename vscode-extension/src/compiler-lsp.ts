/**
 * LSP-based Dashboard Compiler using vscode-languageclient
 *
 * This is a proof-of-concept implementation showing how the dashboard compiler
 * could be implemented using the Language Server Protocol.
 */

import * as path from 'path';
import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind,
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

    async start(): Promise<void> {
        if (this.client) {
            return; // Already started
        }

        const config = vscode.workspace.getConfiguration('yamlDashboard');
        const pythonPath = config.get<string>('pythonPath', 'python');

        // Path to the LSP server script
        const extensionPath = this.context.extensionPath;
        const serverScript = path.join(extensionPath, 'python', 'compile_server_lsp.py');

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
                fileEvents: vscode.workspace.createFileSystemWatcher('**/*.yaml'),
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

        // Register custom notification handler for file changes
        this.client.onReady().then(() => {
            if (!this.client) return;

            // Handle custom notifications from the server
            this.client.onNotification('dashboard/fileChanged', (params: { uri: string }) => {
                this.outputChannel.appendLine(`Dashboard file changed: ${params.uri}`);
                // Could trigger automatic recompilation here
            });
        });

        // Start the client (this will also start the server)
        await this.client.start();
    }

    /**
     * Compile a dashboard using the custom LSP method approach.
     * This is cleaner but requires custom protocol support.
     */
    async compile(filePath: string, dashboardIndex: number = 0): Promise<CompiledDashboard> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        // Wait for client to be ready
        await this.client.onReady();

        // Method 1: Use custom request (cleaner, but non-standard LSP)
        const result = await this.client.sendRequest<CompileResult>(
            'dashboard/compile',
            { path: filePath, dashboard_index: dashboardIndex }
        );

        if (!result.success) {
            throw new Error(result.error || 'Compilation failed');
        }

        return result.data as CompiledDashboard;
    }

    /**
     * Compile a dashboard using the standard workspace/executeCommand approach.
     * This is the "official" LSP way but more verbose.
     */
    async compileViaCommand(filePath: string, dashboardIndex: number = 0): Promise<CompiledDashboard> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        await this.client.onReady();

        // Method 2: Use workspace/executeCommand (standard LSP, but more verbose)
        const result = await this.client.sendRequest<CompileResult>(
            'workspace/executeCommand',
            {
                command: 'dashboard.compile',
                arguments: [filePath, dashboardIndex]
            }
        );

        if (!result.success) {
            throw new Error(result.error || 'Compilation failed');
        }

        return result.data as CompiledDashboard;
    }

    /**
     * Get list of dashboards from a YAML file.
     */
    async getDashboards(filePath: string): Promise<DashboardInfo[]> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        await this.client.onReady();

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

/**
 * Comparison: Current vs LSP Implementation
 *
 * CURRENT IMPLEMENTATION (compile.ts):
 * - Manual stdio handling with child_process.spawn
 * - Custom JSON-RPC protocol (line-delimited JSON)
 * - Manual request/response matching with IDs
 * - Manual timeout handling
 * - Manual error handling
 * - ~195 lines of code
 *
 * LSP IMPLEMENTATION (this file):
 * - vscode-languageclient handles all communication
 * - Standard LSP protocol (or custom extensions)
 * - Automatic request/response matching
 * - Built-in timeout handling
 * - Structured error types
 * - ~180 lines of code (but much simpler logic)
 *
 * BENEFITS OF LSP:
 * ✅ Auto-restart on server crash (handled by LanguageClient)
 * ✅ Structured logging via OutputChannel
 * ✅ File watching built-in (synchronize.fileEvents)
 * ✅ Bidirectional notifications (server can notify client)
 * ✅ Can add diagnostics (real-time validation)
 * ✅ Can add more LSP features later (hover, autocomplete, etc.)
 * ✅ Industry-standard protocol
 *
 * TRADEOFFS:
 * ❌ New dependencies: vscode-languageclient, pygls, lsprotocol
 * ❌ More boilerplate in Python (but pygls handles most of it)
 * ❌ Custom methods still require non-standard protocol extensions
 * ❌ No built-in chunking (still need to handle large responses manually)
 *
 * FILE WATCHING EXAMPLE:
 * With LSP, you can automatically recompile on save:
 *
 * 1. Client registers file watcher (see clientOptions.synchronize above)
 * 2. When user saves YAML file, LSP sends textDocument/didSave
 * 3. Server receives notification, processes it
 * 4. Server sends custom notification back: dashboard/fileChanged
 * 5. Client receives notification, triggers recompilation
 *
 * This is all handled by the LSP infrastructure - no manual file watching needed.
 */
