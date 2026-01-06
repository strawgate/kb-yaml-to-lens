import * as vscode from 'vscode';
import * as path from 'path';
import { DashboardCompilerLSP, CompiledDashboard, DashboardGridInfo } from './compiler';
import { escapeHtml, getLoadingContent, getErrorContent } from './webviewUtils';

export class PreviewPanel {
    private static readonly gridColumns = 48;
    private static readonly scaleFactor = 10; // pixels per grid unit

    private panel: vscode.WebviewPanel | undefined;
    private currentDashboardPath: string | undefined;
    private currentDashboardIndex: number = 0;

    constructor(private compiler: DashboardCompilerLSP) {
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
                gridInfo = await this.compiler.getGridLayout(dashboardPath, dashboardIndex);
            } catch (gridError) {
                console.warn('Grid extraction failed, showing preview without layout:', gridError);
            }
            this.panel.webview.html = this.getWebviewContent(compiled, dashboardPath, gridInfo);
        } catch (error) {
            this.panel.webview.html = getErrorContent(error, 'Compilation Error');
        }
    }

    private getWebviewContent(dashboard: CompiledDashboard, filePath: string, gridInfo: DashboardGridInfo): string {
        // Cast to any for property access since CompiledDashboard structure is dynamic
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const dashboardData = dashboard as any;
        const fileName = path.basename(filePath);
        const ndjson = JSON.stringify(dashboard);
        const layoutHtml = this.generateLayoutHtml(gridInfo);
        const jsonFieldsHtml = this.generateJsonFieldsHtml(dashboardData);

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
                    .panel-header {
                        display: flex;
                        align-items: center;
                        gap: 4px;
                        margin-bottom: 4px;
                    }
                    .panel-icon {
                        font-size: 16px;
                        flex-shrink: 0;
                    }
                    .panel-type-label {
                        font-size: 9px;
                        color: var(--vscode-descriptionForeground);
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    }
                    .panel-title {
                        font-weight: 600;
                        font-size: 11px;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        margin-bottom: 2px;
                    }
                    .panel-size {
                        font-size: 9px;
                        color: var(--vscode-descriptionForeground);
                        font-family: monospace;
                        margin-top: auto;
                    }
                    .collapsible-section {
                        margin-bottom: 20px;
                    }
                    .collapsible-header {
                        cursor: pointer;
                        user-select: none;
                        padding: 10px;
                        background: var(--vscode-editor-selectionBackground);
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 3px;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }
                    .collapsible-header:hover {
                        background: var(--vscode-list-hoverBackground);
                    }
                    .collapsible-arrow {
                        font-size: 12px;
                        transition: transform 0.2s;
                    }
                    .collapsible-arrow.expanded {
                        transform: rotate(90deg);
                    }
                    .collapsible-content {
                        display: none;
                        margin-top: 10px;
                    }
                    .collapsible-content.expanded {
                        display: block;
                    }
                    .json-field-section pre {
                        max-height: 400px;
                        overflow-y: auto;
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
                    <div class="section-title">Dashboard Layout</div>
                    ${layoutHtml}
                </div>

                ${jsonFieldsHtml}

                <div class="section">
                    <div class="section-title">Compiled NDJSON Output</div>
                    <pre><code>${escapeHtml(JSON.stringify(dashboard, null, 2))}</code></pre>
                </div>

                <script>
                    const ndjsonData = ${JSON.stringify(ndjson)};

                    function toggleCollapsible(id) {
                        const content = document.getElementById(id);
                        const arrow = document.getElementById(id + '-arrow');
                        if (content && arrow) {
                            content.classList.toggle('expanded');
                            arrow.classList.toggle('expanded');
                        }
                    }

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

    private generateJsonFieldsHtml(dashboardData: Record<string, unknown>): string {
        const sections: Array<{ id: string; title: string; json: string | null }> = [];

        // Extract panelsJSON
        const panelsJSON = this.getNestedProperty(dashboardData, 'attributes.panelsJSON');
        if (panelsJSON && typeof panelsJSON === 'string') {
            sections.push({
                id: 'panels-json',
                title: 'Panels JSON',
                json: panelsJSON,
            });
        }

        // Extract optionsJSON
        const optionsJSON = this.getNestedProperty(dashboardData, 'attributes.optionsJSON');
        if (optionsJSON && typeof optionsJSON === 'string') {
            sections.push({
                id: 'options-json',
                title: 'Options JSON',
                json: optionsJSON,
            });
        }

        // Extract controlGroupInput.panelsJSON (controls)
        const controlsJSON = this.getNestedProperty(dashboardData, 'attributes.controlGroupInput.panelsJSON');
        if (controlsJSON && typeof controlsJSON === 'string') {
            sections.push({
                id: 'controls-json',
                title: 'Controls JSON',
                json: controlsJSON,
            });
        }

        if (sections.length === 0) {
            return '';
        }

        let html = '<div class="section"><div class="section-title">Dashboard JSON Fields</div>';

        for (const section of sections) {
            if (section.json === null) {
                continue;
            }

            let formattedJson: string;
            try {
                const parsed = JSON.parse(section.json);
                formattedJson = JSON.stringify(parsed, null, 2);
            } catch {
                formattedJson = section.json;
            }

            html += `
                <div class="collapsible-section json-field-section">
                    <div class="collapsible-header" onclick="toggleCollapsible('${section.id}')">
                        <span class="collapsible-arrow" id="${section.id}-arrow">▶</span>
                        <span>${escapeHtml(section.title)}</span>
                    </div>
                    <div class="collapsible-content" id="${section.id}">
                        <pre><code>${escapeHtml(formattedJson)}</code></pre>
                    </div>
                </div>
            `;
        }

        html += '</div>';
        return html;
    }

    private getNestedProperty(obj: Record<string, unknown>, path: string): unknown {
        const parts = path.split('.');
        let current: unknown = obj;

        for (const part of parts) {
            if (current === null || current === undefined || typeof current !== 'object') {
                return undefined;
            }
            current = (current as Record<string, unknown>)[part];
        }

        return current;
    }

    private generateLayoutHtml(gridInfo: DashboardGridInfo): string {
        if (!gridInfo.panels || gridInfo.panels.length === 0) {
            return '<div class="layout-container" style="padding: 20px; text-align: center; color: var(--vscode-descriptionForeground);">No panels in this dashboard</div>';
        }

        // Calculate the height based on panel positions and generate HTML in a single pass
        let maxY = 0;
        let panelsHtml = '';

        for (const panel of gridInfo.panels) {
            // Validate grid properties to prevent invalid CSS
            if (!panel.grid ||
                typeof panel.grid.x !== 'number' ||
                typeof panel.grid.y !== 'number' ||
                typeof panel.grid.w !== 'number' ||
                typeof panel.grid.h !== 'number') {
                console.warn('Skipping panel with invalid grid data:', panel);
                continue;
            }

            // Calculate maxY
            const panelBottom = panel.grid.y + panel.grid.h;
            if (panelBottom > maxY) {
                maxY = panelBottom;
            }

            // Generate panel HTML
            const left = (panel.grid.x / PreviewPanel.gridColumns) * 100;
            const top = panel.grid.y * PreviewPanel.scaleFactor;
            const width = (panel.grid.w / PreviewPanel.gridColumns) * 100;
            const height = panel.grid.h * PreviewPanel.scaleFactor;

            const icon = this.getChartTypeIcon(panel.type);
            const typeLabel = this.getChartTypeLabel(panel.type);

            panelsHtml += `
                <div class="layout-panel" style="left: ${left}%; top: ${top}px; width: ${width}%; height: ${height}px;" title="${escapeHtml(panel.title)} (${typeLabel})">
                    <div class="panel-header">
                        <span class="panel-icon">${icon}</span>
                        <span class="panel-type-label">${escapeHtml(typeLabel)}: ${escapeHtml(panel.title || 'Untitled')}</span>
                    </div>
                    <span class="panel-size">${panel.grid.w}x${panel.grid.h}</span>
                </div>
            `;
        }

        const containerHeight = maxY * PreviewPanel.scaleFactor;

        return `
            <div class="layout-container" style="height: ${containerHeight}px; width: 100%;">
                ${panelsHtml}
            </div>
        `;
    }

}
