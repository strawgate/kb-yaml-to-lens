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
import {
    parseCompileResult,
    parseDashboardListResult,
    parseGridLayoutResult,
    parseUploadResult,
    parseEsqlExecuteResult,
    parseUpdateGridLayoutResult,
    SchemaResult as SchemaResultSchema,
    type DashboardInfoType,
    type DashboardGridInfoType,
    type EsqlResponseType,
    type GridType,
    type SchemaResultType,
} from './schemas';

// Re-export types from schemas for backwards compatibility
export type {
    DashboardInfoType as DashboardInfo,
    DashboardGridInfoType as DashboardGridInfo,
    PanelGridInfoType as PanelGridInfo,
    EsqlColumnType as EsqlColumn,
    EsqlResponseType as EsqlQueryResult,
    GridType as Grid,
} from './schemas';

// Interface for the compiled dashboard result
export type CompiledDashboard = unknown;

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

        const result = await this.client.sendRequest(
            'dashboard/compile',
            // eslint-disable-next-line @typescript-eslint/naming-convention
            { path: filePath, dashboard_index: dashboardIndex }
        );

        return parseCompileResult(result);
    }

    /**
     * Get list of dashboards from a YAML file.
     *
     * @param filePath Path to the YAML file
     * @returns Array of dashboard information objects
     */
    async getDashboards(filePath: string): Promise<DashboardInfoType[]> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        const result = await this.client.sendRequest(
            'dashboard/getDashboards',
            { path: filePath }
        );

        return parseDashboardListResult(result);
    }

    /**
     * Get grid layout information from a YAML dashboard file.
     *
     * @param filePath Path to the YAML file
     * @param dashboardIndex Index of the dashboard to extract (default: 0)
     * @returns Grid layout information
     */
    async getGridLayout(filePath: string, dashboardIndex: number = 0): Promise<DashboardGridInfoType> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        const result = await this.client.sendRequest(
            'dashboard/getGridLayout',
            // eslint-disable-next-line @typescript-eslint/naming-convention
            { path: filePath, dashboard_index: dashboardIndex }
        );

        return parseGridLayoutResult(result);
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

        const result = await this.client.sendRequest(
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

        return parseUploadResult(result);
    }

    /**
     * Update grid coordinates for a specific panel in a YAML dashboard file.
     *
     * @param filePath Path to the YAML file
     * @param panelId ID of the panel to update
     * @param grid New grid coordinates
     * @param dashboardIndex Index of the dashboard (default: 0)
     */
    async updateGridLayout(filePath: string, panelId: string, grid: GridType, dashboardIndex: number = 0): Promise<void> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        const result = await this.client.sendRequest(
            'dashboard/updateGridLayout',
            {
                path: filePath,
                // eslint-disable-next-line @typescript-eslint/naming-convention
                panel_id: panelId,
                grid: grid,
                // eslint-disable-next-line @typescript-eslint/naming-convention
                dashboard_index: dashboardIndex
            }
        );

        parseUpdateGridLayoutResult(result);
    }

    /**
     * Get the JSON schema for dashboard YAML files.
     * This schema is used for auto-complete and validation in the YAML editor.
     *
     * @returns Schema result with success status and schema data
     */
    async getSchema(): Promise<SchemaResultType> {
        if (!this.client) {
            return { success: false, data: null, error: 'LSP client not started' };
        }

        try {
            const result = await this.client.sendRequest('dashboard/getSchema', {});
            return SchemaResultSchema.parse(result);
        } catch (error) {
            return { success: false, data: null, error: error instanceof Error ? error.message : String(error) };
        }
    }

    /**
     * Execute an ES|QL query via Kibana's console proxy API.
     *
     * @param query The ES|QL query string to execute
     * @param kibanaUrl Kibana base URL
     * @param username Optional username for basic auth
     * @param password Optional password for basic auth
     * @param apiKey Optional API key for auth
     * @param sslVerify Whether to verify SSL certificates
     * @returns Object containing columns and values from query results
     */
    async executeEsqlQuery(
        query: string,
        kibanaUrl: string,
        username: string,
        password: string,
        apiKey: string,
        sslVerify: boolean
    ): Promise<EsqlResponseType> {
        if (!this.client) {
            throw new Error('LSP client not started');
        }

        const result = await this.client.sendRequest(
            'esql/execute',
            {
                query: query,
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

        return parseEsqlExecuteResult(result);
    }

    async dispose(): Promise<void> {
        if (this.client) {
            await this.client.stop();
            this.client = null;
        }
        this.outputChannel.dispose();
    }
}
