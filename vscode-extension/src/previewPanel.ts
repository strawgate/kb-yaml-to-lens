import * as vscode from 'vscode';
import * as path from 'path';
import { DashboardCompiler, CompiledDashboard } from './compiler';

export class PreviewPanel {
    private panel: vscode.WebviewPanel | undefined;
    private currentDashboardPath: string | undefined;

    constructor(private compiler: DashboardCompiler) {}

    async show(dashboardPath: string) {
        this.currentDashboardPath = dashboardPath;

        if (!this.panel) {
            this.panel = vscode.window.createWebviewPanel(
                'dashboardPreview',
                'Dashboard Preview',
                vscode.ViewColumn.Beside,
                {
                    enableScripts: true,
                    retainContextWhenHidden: true
                }
            );

            this.panel.onDidDispose(() => {
                this.panel = undefined;
            });
        }

        await this.updatePreview(dashboardPath);
    }

    async updatePreview(dashboardPath: string) {
        if (!this.panel) {
            return;
        }

        // Only update if this is the currently previewed dashboard
        if (this.currentDashboardPath !== dashboardPath) {
            return;
        }

        this.panel.webview.html = this.getLoadingContent();

        try {
            const compiled = await this.compiler.compile(dashboardPath);
            this.panel.webview.html = this.getWebviewContent(compiled, dashboardPath);
        } catch (error) {
            this.panel.webview.html = this.getErrorContent(error);
        }
    }

    private getLoadingContent(): string {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {
                        font-family: var(--vscode-font-family);
                        padding: 20px;
                        background: var(--vscode-editor-background);
                        color: var(--vscode-editor-foreground);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .loading {
                        text-align: center;
                    }
                </style>
            </head>
            <body>
                <div class="loading">
                    <h2>Compiling dashboard...</h2>
                </div>
            </body>
            </html>
        `;
    }

    private getWebviewContent(dashboard: CompiledDashboard, filePath: string): string {
        // Cast to any for property access since CompiledDashboard structure is dynamic
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const dashboardData = dashboard as any;
        const fileName = path.basename(filePath);
        const ndjson = JSON.stringify(dashboard);

        return `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {
                        font-family: var(--vscode-font-family);
                        padding: 20px;
                        background: var(--vscode-editor-background);
                        color: var(--vscode-editor-foreground);
                        margin: 0;
                    }
                    .header {
                        border-bottom: 1px solid var(--vscode-panel-border);
                        padding-bottom: 20px;
                        margin-bottom: 20px;
                    }
                    .title {
                        font-size: 24px;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }
                    .file-path {
                        color: var(--vscode-descriptionForeground);
                        font-size: 12px;
                        margin-bottom: 15px;
                    }
                    .actions {
                        margin-top: 15px;
                    }
                    .export-btn {
                        background: var(--vscode-button-background);
                        color: var(--vscode-button-foreground);
                        border: none;
                        padding: 8px 16px;
                        cursor: pointer;
                        border-radius: 2px;
                        font-family: var(--vscode-font-family);
                        font-size: 13px;
                        margin-right: 8px;
                    }
                    .export-btn:hover {
                        background: var(--vscode-button-hoverBackground);
                    }
                    .export-btn:active {
                        background: var(--vscode-button-activeBackground);
                    }
                    .section {
                        margin-bottom: 20px;
                    }
                    .section-title {
                        font-size: 16px;
                        font-weight: bold;
                        margin-bottom: 10px;
                        color: var(--vscode-settings-headerForeground);
                    }
                    .info-grid {
                        display: grid;
                        grid-template-columns: 150px 1fr;
                        gap: 10px;
                        margin-bottom: 20px;
                    }
                    .info-label {
                        color: var(--vscode-descriptionForeground);
                    }
                    .info-value {
                        color: var(--vscode-editor-foreground);
                    }
                    pre {
                        background: var(--vscode-textCodeBlock-background);
                        padding: 15px;
                        border-radius: 3px;
                        overflow-x: auto;
                        border: 1px solid var(--vscode-panel-border);
                    }
                    code {
                        font-family: var(--vscode-editor-font-family);
                        font-size: var(--vscode-editor-font-size);
                    }
                    .success-message {
                        background: var(--vscode-inputValidation-infoBackground);
                        border: 1px solid var(--vscode-inputValidation-infoBorder);
                        color: var(--vscode-inputValidation-infoForeground);
                        padding: 10px;
                        border-radius: 3px;
                        margin-top: 10px;
                        display: none;
                    }
                    .success-message.show {
                        display: block;
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="title">${this.escapeHtml(dashboardData.attributes?.title || 'Dashboard')}</div>
                    <div class="file-path">${this.escapeHtml(fileName)}</div>
                    <div class="actions">
                        <button class="export-btn" onclick="copyToClipboard()">
                            Copy NDJSON for Kibana Import
                        </button>
                        <button class="export-btn" onclick="downloadNDJSON()">
                            Download NDJSON
                        </button>
                    </div>
                    <div class="success-message" id="successMessage">
                        ✓ Copied to clipboard! Import in Kibana: Stack Management → Saved Objects → Import
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">Dashboard Information</div>
                    <div class="info-grid">
                        <div class="info-label">Type:</div>
                        <div class="info-value">${this.escapeHtml(dashboardData.type || 'N/A')}</div>
                        <div class="info-label">ID:</div>
                        <div class="info-value">${this.escapeHtml(dashboardData.id || 'N/A')}</div>
                        <div class="info-label">Version:</div>
                        <div class="info-value">${this.escapeHtml(dashboardData.version || 'N/A')}</div>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">Compiled NDJSON Output</div>
                    <pre><code>${this.escapeHtml(JSON.stringify(dashboard, null, 2))}</code></pre>
                </div>

                <script>
                    const ndjsonData = ${JSON.stringify(ndjson)};

                    function copyToClipboard() {
                        navigator.clipboard.writeText(ndjsonData).then(() => {
                            const message = document.getElementById('successMessage');
                            message.classList.add('show');
                            setTimeout(() => {
                                message.classList.remove('show');
                            }, 3000);
                        }).catch((err) => {
                            console.error('Failed to copy:', err);
                            alert('Failed to copy to clipboard: ' + err.message);
                        });
                    }

                    function downloadNDJSON() {
                        const blob = new Blob([ndjsonData], { type: 'application/x-ndjson' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = '${this.escapeHtml(fileName.replace('.yaml', '.ndjson'))}';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                    }
                </script>
            </body>
            </html>
        `;
    }

    private getErrorContent(error: unknown): string {
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {
                        font-family: var(--vscode-font-family);
                        padding: 20px;
                        background: var(--vscode-editor-background);
                        color: var(--vscode-errorForeground);
                    }
                    h2 {
                        margin-top: 0;
                    }
                    pre {
                        background: var(--vscode-textCodeBlock-background);
                        padding: 15px;
                        border-radius: 3px;
                        overflow-x: auto;
                        border: 1px solid var(--vscode-inputValidation-errorBorder);
                    }
                </style>
            </head>
            <body>
                <h2>Compilation Error</h2>
                <pre>${this.escapeHtml(error instanceof Error ? error.message : String(error))}</pre>
            </body>
            </html>
        `;
    }

    private escapeHtml(text: string): string {
        return text.replace(/[&<>"']/g, (char) => {
            switch (char) {
                case '&': return '&amp;';
                case '<': return '&lt;';
                case '>': return '&gt;';
                case '"': return '&quot;';
                case "'": return '&#039;';
                default: return char;
            }
        });
    }
}
