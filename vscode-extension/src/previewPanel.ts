import * as vscode from 'vscode';
import * as path from 'path';
import { DashboardCompilerLSP, CompiledDashboard } from './compiler';
import { escapeHtml, getLoadingContent, getErrorContent } from './webviewUtils';

export class PreviewPanel {
    private panel: vscode.WebviewPanel | undefined;
    private currentDashboardPath: string | undefined;
    private currentDashboardIndex: number = 0;

    constructor(private compiler: DashboardCompilerLSP) {}

    async show(dashboardPath: string, dashboardIndex: number = 0) {
        this.currentDashboardPath = dashboardPath;
        this.currentDashboardIndex = dashboardIndex;

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

        await this.updatePreview(dashboardPath, dashboardIndex);
    }

    async updatePreview(dashboardPath: string, dashboardIndex: number = 0) {
        if (!this.panel) {
            return;
        }

        // Only update if this is the currently previewed dashboard
        if (this.currentDashboardPath !== dashboardPath || this.currentDashboardIndex !== dashboardIndex) {
            return;
        }

        this.panel.webview.html = getLoadingContent('Compiling dashboard...');

        try {
            const compiled = await this.compiler.compile(dashboardPath, dashboardIndex);
            this.panel.webview.html = this.getWebviewContent(compiled, dashboardPath);
        } catch (error) {
            this.panel.webview.html = getErrorContent(error, 'Compilation Error');
        }
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
                    <div class="title">${escapeHtml(dashboardData.attributes?.title || 'Dashboard')}</div>
                    <div class="file-path">${escapeHtml(fileName)}</div>
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
                        <div class="info-value">${escapeHtml(dashboardData.type || 'N/A')}</div>
                        <div class="info-label">ID:</div>
                        <div class="info-value">${escapeHtml(dashboardData.id || 'N/A')}</div>
                        <div class="info-label">Version:</div>
                        <div class="info-value">${escapeHtml(dashboardData.version || 'N/A')}</div>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">Compiled NDJSON Output</div>
                    <pre><code>${escapeHtml(JSON.stringify(dashboard, null, 2))}</code></pre>
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
                        a.download = '${escapeHtml(fileName.replace('.yaml', '.ndjson'))}';
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

}
