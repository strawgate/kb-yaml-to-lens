import * as vscode from 'vscode';
import * as path from 'path';
import { spawn } from 'child_process';
import { DashboardCompilerLSP, CompiledDashboard } from './compiler';
import { escapeHtml, getLoadingContent, getErrorContent } from './webviewUtils';
import { ConfigService } from './configService';

interface PanelGridInfo {
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

interface DashboardGridInfo {
    title: string;
    description: string;
    panels: PanelGridInfo[];
}

export class PreviewPanel {
    private panel: vscode.WebviewPanel | undefined;
    private currentDashboardPath: string | undefined;
    private currentDashboardIndex: number = 0;
    private extensionPath: string;

    constructor(private compiler: DashboardCompilerLSP, context: vscode.ExtensionContext) {
        this.extensionPath = context.extensionPath;
    }

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
            let gridInfo: DashboardGridInfo = { title: '', description: '', panels: [] };
            try {
                gridInfo = await this.extractGridInfo(dashboardPath, dashboardIndex);
            } catch (gridError) {
                console.warn('Grid extraction failed, showing preview without layout:', gridError);
            }
            this.panel.webview.html = this.getWebviewContent(compiled, dashboardPath, gridInfo);
        } catch (error) {
            this.panel.webview.html = getErrorContent(error, 'Compilation Error');
        }
    }

    private async extractGridInfo(dashboardPath: string, dashboardIndex: number = 0): Promise<DashboardGridInfo> {
        const pythonPath = ConfigService.getPythonPath();
        const scriptPath = path.join(this.extensionPath, 'python', 'grid_extractor.py');

        return new Promise((resolve, reject) => {
            let settled = false;
            const process = spawn(pythonPath, [scriptPath, dashboardPath, dashboardIndex.toString()], {
                cwd: path.join(this.extensionPath, '..')
            });

            let stdout = '';
            let stderr = '';

            const timeout = setTimeout(() => {
                process.kill();
                if (!settled) {
                    settled = true;
                    reject(new Error('Grid extraction timed out after 30 seconds'));
                }
            }, 30000);

            process.on('error', (err) => {
                clearTimeout(timeout);
                if (!settled) {
                    settled = true;
                    reject(new Error(`Failed to start Python: ${err.message}`));
                }
            });

            process.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            process.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            process.on('close', (code) => {
                clearTimeout(timeout);
                if (settled) {
                    return;
                }
                settled = true;
                if (code !== 0) {
                    reject(new Error(`Grid extraction failed: ${stderr || stdout}`));
                    return;
                }

                try {
                    const result = JSON.parse(stdout);
                    if (result.error) {
                        reject(new Error(result.error));
                    } else {
                        resolve(result);
                    }
                } catch (error) {
                    reject(new Error(`Failed to parse grid info: ${error}`));
                }
            });
        });
    }

    private getWebviewContent(dashboard: CompiledDashboard, filePath: string, gridInfo: DashboardGridInfo): string {
        // Cast to any for property access since CompiledDashboard structure is dynamic
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const dashboardData = dashboard as any;
        const fileName = path.basename(filePath);
        const ndjson = JSON.stringify(dashboard);
        const layoutHtml = this.generateLayoutHtml(gridInfo);

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

                    /* Layout Preview Styles */
                    .layout-container {
                        position: relative;
                        width: 100%;
                        background: var(--vscode-textCodeBlock-background);
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 4px;
                        overflow: hidden;
                    }
                    .layout-panel {
                        position: absolute;
                        background: var(--vscode-editor-selectionBackground);
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 3px;
                        padding: 8px;
                        box-sizing: border-box;
                        overflow: hidden;
                        display: flex;
                        flex-direction: column;
                    }
                    .layout-panel:hover {
                        background: var(--vscode-list-hoverBackground);
                        border-color: var(--vscode-focusBorder);
                    }
                    .panel-icon {
                        font-size: 16px;
                        margin-bottom: 4px;
                    }
                    .panel-title {
                        font-weight: 600;
                        font-size: 11px;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        margin-bottom: 2px;
                    }
                    .panel-type-label {
                        font-size: 10px;
                        color: var(--vscode-descriptionForeground);
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    }
                    .panel-size {
                        font-size: 9px;
                        color: var(--vscode-descriptionForeground);
                        font-family: monospace;
                        margin-top: auto;
                    }
                    .layout-legend {
                        margin-top: 15px;
                        padding: 12px;
                        background: var(--vscode-textCodeBlock-background);
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 4px;
                    }
                    .legend-title {
                        font-size: 12px;
                        font-weight: 600;
                        margin-bottom: 8px;
                        color: var(--vscode-descriptionForeground);
                    }
                    .legend-items {
                        display: flex;
                        flex-wrap: wrap;
                        gap: 12px;
                    }
                    .legend-item {
                        display: flex;
                        align-items: center;
                        gap: 4px;
                        font-size: 11px;
                    }
                    .legend-icon {
                        font-size: 14px;
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
                        Copied to clipboard! Import in Kibana: Stack Management > Saved Objects > Import
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">Dashboard Layout</div>
                    ${layoutHtml}
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

    private getChartTypeIcon(type: string): string {
        const icons: Record<string, string> = {
            // Chart types
            'line': '\u{1F4C8}',      // chart increasing
            'bar': '\u{1F4CA}',       // bar chart
            'area': '\u{1F5FB}',      // mountain (area chart)
            'pie': '\u{1F967}',       // pie
            'metric': '\u{0023}\u{FE0F}\u{20E3}', // keycap #
            'gauge': '\u{1F3AF}',     // target/gauge
            'datatable': '\u{1F4CB}', // clipboard (table)
            'tagcloud': '\u{2601}\u{FE0F}', // cloud
            // Non-chart types
            'markdown': '\u{1F4DD}',  // memo
            'search': '\u{1F50D}',    // magnifying glass
            'links': '\u{1F517}',     // link
            'image': '\u{1F5BC}\u{FE0F}', // framed picture
            // ESQL variants (same icons as lens)
            'esqlmetric': '\u{0023}\u{FE0F}\u{20E3}',
            'esqlgauge': '\u{1F3AF}',
            'esqlpie': '\u{1F967}',
            'esqlbar': '\u{1F4CA}',
            'esqlline': '\u{1F4C8}',
            'esqlarea': '\u{1F5FB}',
            'esqldatatable': '\u{1F4CB}',
            'esqltagcloud': '\u{2601}\u{FE0F}',
        };
        return icons[type.toLowerCase()] || '\u{1F4C4}'; // default: page facing up
    }

    private getChartTypeLabel(type: string): string {
        const labels: Record<string, string> = {
            'line': 'Line Chart',
            'bar': 'Bar Chart',
            'area': 'Area Chart',
            'pie': 'Pie Chart',
            'metric': 'Metric',
            'gauge': 'Gauge',
            'datatable': 'Data Table',
            'tagcloud': 'Tag Cloud',
            'markdown': 'Markdown',
            'search': 'Search',
            'links': 'Links',
            'image': 'Image',
            'esqlmetric': 'ES|QL Metric',
            'esqlgauge': 'ES|QL Gauge',
            'esqlpie': 'ES|QL Pie',
            'esqlbar': 'ES|QL Bar',
            'esqlline': 'ES|QL Line',
            'esqlarea': 'ES|QL Area',
            'esqldatatable': 'ES|QL Table',
            'esqltagcloud': 'ES|QL Cloud',
        };
        return labels[type.toLowerCase()] || type;
    }

    private generateLayoutHtml(gridInfo: DashboardGridInfo): string {
        if (!gridInfo.panels || gridInfo.panels.length === 0) {
            return '<div class="layout-container" style="padding: 20px; text-align: center; color: var(--vscode-descriptionForeground);">No panels in this dashboard</div>';
        }

        const GRID_COLUMNS = 48;
        const SCALE_FACTOR = 10; // pixels per grid unit

        // Calculate the height based on panel positions
        let maxY = 0;
        for (const panel of gridInfo.panels) {
            const panelBottom = panel.grid.y + panel.grid.h;
            if (panelBottom > maxY) {
                maxY = panelBottom;
            }
        }
        const containerHeight = maxY * SCALE_FACTOR;
        const containerWidth = GRID_COLUMNS * SCALE_FACTOR;

        // Generate panel HTML
        let panelsHtml = '';
        const usedTypes = new Set<string>();

        for (const panel of gridInfo.panels) {
            const left = (panel.grid.x / GRID_COLUMNS) * 100;
            const top = panel.grid.y * SCALE_FACTOR;
            const width = (panel.grid.w / GRID_COLUMNS) * 100;
            const height = panel.grid.h * SCALE_FACTOR;

            const icon = this.getChartTypeIcon(panel.type);
            const typeLabel = this.getChartTypeLabel(panel.type);
            usedTypes.add(panel.type.toLowerCase());

            panelsHtml += `
                <div class="layout-panel" style="left: ${left}%; top: ${top}px; width: ${width}%; height: ${height}px;" title="${escapeHtml(panel.title)} (${typeLabel})">
                    <span class="panel-icon">${icon}</span>
                    <span class="panel-title">${escapeHtml(panel.title || 'Untitled')}</span>
                    <span class="panel-type-label">${escapeHtml(typeLabel)}</span>
                    <span class="panel-size">${panel.grid.w}x${panel.grid.h}</span>
                </div>
            `;
        }

        // Generate legend for used types
        let legendItems = '';
        for (const type of usedTypes) {
            const icon = this.getChartTypeIcon(type);
            const label = this.getChartTypeLabel(type);
            legendItems += `
                <div class="legend-item">
                    <span class="legend-icon">${icon}</span>
                    <span>${escapeHtml(label)}</span>
                </div>
            `;
        }

        return `
            <div class="layout-container" style="height: ${containerHeight}px; width: ${containerWidth}px; max-width: 100%;">
                ${panelsHtml}
            </div>
            <div class="layout-legend">
                <div class="legend-title">Panel Types</div>
                <div class="legend-items">
                    ${legendItems}
                </div>
            </div>
        `;
    }

}
