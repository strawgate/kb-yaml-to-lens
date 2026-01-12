/**
 * LSP-based Dashboard Compiler using vscode-languageclient
 *
 * This implementation uses the Language Server Protocol to provide
 * dashboard compilation services to the VS Code extension.
 */

import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
} from 'vscode-languageclient/node';
import { ConfigService } from './configService';
import { BinaryResolver } from './binaryResolver';

// Interface for the compiled dashboard result
export type CompiledDashboard = unknown;

export interface DashboardInfo {
    index: number;
    title: string;
    description: string;
}

export interface PanelGridInfo {
    id: string;
    title: string;
    type: string;
    grid: {
        x: number;
        y: number;
        w: number;
        h: number;
    };
}

export interface DashboardGridInfo {
    title: string;
    description: string;
    panels: PanelGridInfo[];
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

interface GridLayoutResult {
    success: boolean;
    data?: DashboardGridInfo;
    error?: string;
}

// Matches Python LSP server response format
interface UploadResult {
    success: boolean;
    // eslint-disable-next-line @typescript-eslint/naming-convention
    dashboard_url?: string;
    // eslint-disable-next-line @typescript-eslint/naming-convention
    dashboard_id?: string;
    error?: string;
}

export class DashboardCompilerLSP {
    private client: LanguageClient | null = null;
    private outputChannel: vscode.OutputChannel;

    constructor(
        private context: vscode.ExtensionContext,
        private configService: ConfigService
    ) {
        this.outputChannel = vscode.window.createOutputChannel('Dashboard Compiler LSP');
    }

    async start(): Promise<void> {
        if (this.client) {
            return; // Already started
        }

        // Resolve LSP server (bundled binary or Python script)
        const resolver = new BinaryResolver(this.context.extensionPath, this.configService);
        const config = resolver.resolveLSPServer(this.outputChannel);

        // Server options - how to start the LSP server
        const serverOptions: ServerOptions = {
            command: config.executable,
            args: config.args,
            options: {
                cwd: config.cwd,
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

        if (result.data === undefined) {
            throw new Error('Compilation returned no data');
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

        if (result.data === undefined) {
            throw new Error('getDashboards returned no data');
        }

        return result.data;
    }

    /**
     * Get grid layout information from a YAML dashboard file.
     *
     * @param filePath Path to the YAML file
     * @param dashboardIndex Index of the dashboard to extract (default: 0)
     * @returns Grid layout information
     */
    async getGridLayout(filePath: string, dashboardIndex: number = 0): Promise<DashboardGridInfo> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        const result = await this.client.sendRequest<GridLayoutResult>(
            'dashboard/getGridLayout',
            // eslint-disable-next-line @typescript-eslint/naming-convention
            { path: filePath, dashboard_index: dashboardIndex }
        );

        if (!result.success) {
            throw new Error(result.error || 'Failed to get grid layout');
        }

        if (result.data === undefined) {
            throw new Error('getGridLayout returned no data');
        }

        return result.data;
    }

    /**
     * Upload a compiled dashboard to Kibana.
     *
     * @param filePath Path to the YAML file
     * @param dashboardIndex Index of the dashboard to upload
     * @param kibanaUrl Kibana base URL
     * @param username Optional username for basic auth
     * @param password Optional password for basic auth
     * @param apiKey Optional API key for auth
     * @param sslVerify Whether to verify SSL certificates
     * @returns Object containing dashboard URL and ID
     */
    async uploadToKibana(
        filePath: string,
        dashboardIndex: number,
        kibanaUrl: string,
        username: string,
        password: string,
        apiKey: string,
        sslVerify: boolean
    ): Promise<{ dashboardUrl: string; dashboardId: string }> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        const result = await this.client.sendRequest<UploadResult>(
            'dashboard/uploadToKibana',
            {
                path: filePath,
                // eslint-disable-next-line @typescript-eslint/naming-convention
                dashboard_index: dashboardIndex,
                // eslint-disable-next-line @typescript-eslint/naming-convention
                kibana_url: kibanaUrl,
                username: username || undefined,
                password: password || undefined,
                // eslint-disable-next-line @typescript-eslint/naming-convention
                api_key: apiKey || undefined,
                // eslint-disable-next-line @typescript-eslint/naming-convention
                ssl_verify: sslVerify
            }
        );

        if (!result.success) {
            throw new Error(result.error || 'Upload failed');
        }

        if (!result.dashboard_url || !result.dashboard_id) {
            throw new Error('Upload succeeded but dashboard URL/ID not returned');
        }

        return {
            dashboardUrl: result.dashboard_url,
            dashboardId: result.dashboard_id
        };
    }

    /**
     * Get the JSON schema for dashboard YAML files.
     * This schema is used for auto-complete and validation in the YAML editor.
     *
     * @returns Schema result with success status and schema data
     */
    async getSchema(): Promise<{ success: boolean; data?: unknown; error?: string }> {
        if (!this.client) {
            return { success: false, error: 'LSP client not started' };
        }

        try {
            return await this.client.sendRequest('dashboard/getSchema', {});
        } catch (error) {
            return { success: false, error: error instanceof Error ? error.message : String(error) };
        }
    }

    async dispose(): Promise<void> {
        if (this.client) {
            await this.client.stop();
            this.client = null;
        }
        this.outputChannel.dispose();
    }
}
