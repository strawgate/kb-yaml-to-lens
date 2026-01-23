import * as vscode from 'vscode';
import * as path from 'path';
import { spawn } from 'child_process';
import { DashboardCompilerLSP, CompiledDashboard, DashboardGridInfo } from './compiler';
import { escapeHtml, getLoadingContent, getErrorContent } from './webviewUtils';
import { ConfigService } from './configService';
import { BinaryResolver } from './binaryResolver';

export class PreviewPanel {
    private static readonly gridColumns = 48;
    private static readonly scaleFactor = 12; // pixels per grid unit (48 cols * 12px = 576px width)

    private static readonly chartTypeRegistry: Record<string, { icon: string; label: string }> = {
        'line': { icon: '\u{1F4C8}', label: 'Line Chart' },
        'bar': { icon: '\u{1F4CA}', label: 'Bar Chart' },
        'area': { icon: '\u{1F5FB}', label: 'Area Chart' },
        'pie': { icon: '\u{1F967}', label: 'Pie Chart' },
        'metric': { icon: '\u{0023}\u{FE0F}\u{20E3}', label: 'Metric' },
        'gauge': { icon: '\u{1F3AF}', label: 'Gauge' },
        'datatable': { icon: '\u{1F4CB}', label: 'Data Table' },
        'tagcloud': { icon: '\u{2601}\u{FE0F}', label: 'Tag Cloud' },
        'markdown': { icon: '\u{1F4DD}', label: 'Markdown' },
        'search': { icon: '\u{1F50D}', label: 'Search' },
        'links': { icon: '\u{1F517}', label: 'Links' },
        'image': { icon: '\u{1F5BC}\u{FE0F}', label: 'Image' },
        'esqlmetric': { icon: '\u{0023}\u{FE0F}\u{20E3}', label: 'ES|QL Metric' },
        'esqlgauge': { icon: '\u{1F3AF}', label: 'ES|QL Gauge' },
        'esqlpie': { icon: '\u{1F967}', label: 'ES|QL Pie' },
        'esqlbar': { icon: '\u{1F4CA}', label: 'ES|QL Bar' },
        'esqlline': { icon: '\u{1F4C8}', label: 'ES|QL Line' },
        'esqlarea': { icon: '\u{1F5FB}', label: 'ES|QL Area' },
        'esqldatatable': { icon: '\u{1F4CB}', label: 'ES|QL Table' },
        'esqltagcloud': { icon: '\u{2601}\u{FE0F}', label: 'ES|QL Cloud' },
    };

    private panel: vscode.WebviewPanel | undefined;
    private currentDashboardPath: string | undefined;
    private currentDashboardIndex: number = 0;
    private extensionPath: string;
    private mediaPath: vscode.Uri;

    constructor(
        private compiler: DashboardCompilerLSP,
        private context: vscode.ExtensionContext,
        private configService: ConfigService
    ) {
        this.extensionPath = context.extensionPath;
        this.mediaPath = vscode.Uri.joinPath(context.extensionUri, 'media');
    }

    /** Get webview URI for a media file */
    private getMediaUri(webview: vscode.Webview, filename: string): vscode.Uri {
        return webview.asWebviewUri(vscode.Uri.joinPath(this.mediaPath, filename));
    }

    dispose(): void {
        if (this.panel) {
            this.panel.dispose();
            this.panel = undefined;
        }
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
                    retainContextWhenHidden: true,
                    localResourceRoots: [this.mediaPath]
                }
            );

            this.panel.onDidDispose(() => {
                this.panel = undefined;
            });

            // Handle messages from the webview (for drag-and-drop updates)
            this.panel.webview.onDidReceiveMessage(
                async message => {
                    switch (message.command) {
                        case 'updateGrid':
                            await this.updatePanelGrid(
                                message.panelId,
                                message.grid
                            );
                            break;
                    }
                },
                undefined,
                this.context.subscriptions
            );
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
                // Use direct Python script call (same as working GridEditorPanel)
                gridInfo = await this.extractGridInfo(dashboardPath, dashboardIndex);
            } catch (gridError) {
                console.warn('Grid extraction failed, showing preview without layout:', gridError);
            }
            this.panel.webview.html = this.getWebviewContent(compiled, dashboardPath, gridInfo);
        } catch (compileError) {
            // Compilation failed - try to show layout-only mode so user can fix layout issues
            try {
                const gridInfo = await this.extractGridInfo(dashboardPath, dashboardIndex);
                const errorMessage = compileError instanceof Error ? compileError.message : String(compileError);
                this.panel.webview.html = this.getLayoutOnlyContent(dashboardPath, gridInfo, errorMessage);
            } catch (gridError) {
                // Both compilation and grid extraction failed - show the original error
                this.panel.webview.html = getErrorContent(compileError, 'Compilation Error');
            }
        }
    }

    private async extractGridInfo(dashboardPath: string, dashboardIndex: number = 0): Promise<DashboardGridInfo> {
        return this.runPythonScript(
            ['-m', 'dashboard_compiler.lsp.grid_extractor', dashboardPath, dashboardIndex.toString()],
            'Grid extraction',
            (stdout) => {
                const result = JSON.parse(stdout.trim());
                if (result.error) {
                    throw new Error(result.error);
                }
                if (!result || typeof result !== 'object' || !Array.isArray(result.panels)) {
                    throw new Error('Invalid grid extractor output (expected { title, description, panels[] })');
                }
                return result;
            }
        );
    }

    private async runPythonScript<T = unknown>(
        args: string[],
        errorContext: string,
        parseResult: (stdout: string) => T,
        timeout: number = 30000
    ): Promise<T> {
        const resolver = new BinaryResolver(this.extensionPath, this.configService);
        const resolved = resolver.resolveForScripts();

        const fullArgs = [...resolved.args, ...args];

        return new Promise((resolve, reject) => {
            let settled = false;
            const settleReject = (err: Error) => {
                if (settled) {
                    return;
                }
                settled = true;
                reject(err);
            };
            const settleResolve = (val: T) => {
                if (settled) {
                    return;
                }
                settled = true;
                resolve(val);
            };

            const child = spawn(resolved.executable, fullArgs, {
                cwd: resolved.isBundled ? resolved.cwd : path.join(this.extensionPath, '..')
            });

            let stdout = '';
            let stderr = '';

            const timeoutHandle = setTimeout(() => {
                try {
                    child.kill();
                } catch {
                    // ignore
                }
                settleReject(new Error(`${errorContext} timed out after ${timeout / 1000} seconds. stderr: ${stderr || '(empty)'}`));
            }, timeout);

            child.on('error', (err) => {
                clearTimeout(timeoutHandle);
                settleReject(new Error(`Failed to start Python: ${err.message}`));
            });

            child.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            child.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            child.on('close', (code) => {
                clearTimeout(timeoutHandle);
                if (settled) {
                    return;
                }
                if (code !== 0) {
                    settleReject(new Error(`${errorContext} failed: ${stderr || stdout}`));
                    return;
                }

                try {
                    settleResolve(parseResult(stdout));
                } catch (error) {
                    settleReject(new Error(`Failed to parse result: ${error instanceof Error ? error.message : String(error)}`));
                }
            });
        });
    }

    private async updatePanelGrid(panelId: string, grid: { x: number; y: number; w: number; h: number }): Promise<void> {
        if (!this.currentDashboardPath) {
            return;
        }

        try {
            await this.runPythonScript(
                ['-m', 'dashboard_compiler.lsp.grid_updater', this.currentDashboardPath, panelId, JSON.stringify(grid), this.currentDashboardIndex.toString()],
                'Grid update',
                (stdout) => stdout
            );
            // Don't refresh preview - the visual state is already correct from the drag,
            // and refreshing causes an annoying "Compiling..." flash. The YAML is updated,
            // and the file watcher will handle recompilation if compileOnSave is enabled.
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to update grid: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    private getWebviewContent(dashboard: CompiledDashboard, filePath: string, gridInfo: DashboardGridInfo): string {
        if (!this.panel) {
            throw new Error('Panel not initialized');
        }
        
        const webview = this.panel.webview;
        const cssUri = this.getMediaUri(webview, 'preview.css');
        const layoutEditorUri = this.getMediaUri(webview, 'layoutEditor.js');
        const previewJsUri = this.getMediaUri(webview, 'preview.js');
        
        // Cast to any for property access since CompiledDashboard structure is dynamic
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const dashboardData = dashboard as any;
        const fileName = path.basename(filePath);
        const downloadFilename = fileName.replace('.yaml', '.ndjson');
        // Escape < to prevent </script> injection in embedded JSON
        const ndjson = JSON.stringify(dashboard).replace(/</g, '\\u003c');
        const layoutHtml = this.generateLayoutHtml(gridInfo);
        const jsonFieldsHtml = this.generateJsonFieldsHtml(dashboardData);
        
        // Configuration for external JS files
        const layoutConfig = JSON.stringify({
            cellSize: PreviewPanel.scaleFactor,
            gridColumns: PreviewPanel.gridColumns,
            panels: gridInfo.panels,
            showStaleWarning: true
        }).replace(/</g, '\\u003c');
        
        const previewConfig = JSON.stringify({
            downloadFilename
        }).replace(/</g, '\\u003c');

        return `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="${cssUri}">
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
                    <div class="stale-warning" id="staleWarning">
                        Layout changed - NDJSON output may be stale. Save the file to recompile.
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
                    <div class="layout-controls">
                        <label class="control-label">
                            <input type="checkbox" id="showGrid" checked> Show Grid Lines
                        </label>
                        <span class="edit-hint">Drag panels to move, drag corners to resize</span>
                    </div>
                    ${layoutHtml}
                </div>

                ${jsonFieldsHtml}

                <div class="section">
                    <div class="section-title">Compiled NDJSON Output</div>
                    <pre><code>${escapeHtml(JSON.stringify(dashboard, null, 2))}</code></pre>
                </div>

                <!-- Configuration data for external scripts -->
                <script id="layout-config" type="application/json">${layoutConfig}</script>
                <script id="preview-config" type="application/json">${previewConfig}</script>
                <script id="ndjson-data" type="application/json">${ndjson}</script>
                
                <!-- External scripts -->
                <script src="${layoutEditorUri}"></script>
                <script src="${previewJsUri}"></script>
            </body>
            </html>
        `;
    }

    /**
     * Returns a degraded view showing only the layout editor when compilation fails.
     * This allows users to fix layout issues (like overlapping panels) even when
     * the dashboard won't compile.
     */
    private getLayoutOnlyContent(filePath: string, gridInfo: DashboardGridInfo, errorMessage: string): string {
        if (!this.panel) {
            throw new Error('Panel not initialized');
        }
        
        const webview = this.panel.webview;
        const cssUri = this.getMediaUri(webview, 'preview.css');
        const layoutEditorUri = this.getMediaUri(webview, 'layoutEditor.js');
        
        const fileName = path.basename(filePath);
        const layoutHtml = this.generateLayoutHtml(gridInfo);
        
        // Configuration for external JS files (no stale warning in layout-only mode)
        const layoutConfig = JSON.stringify({
            cellSize: PreviewPanel.scaleFactor,
            gridColumns: PreviewPanel.gridColumns,
            panels: gridInfo.panels,
            showStaleWarning: false
        }).replace(/</g, '\\u003c');

        return `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="${cssUri}">
            </head>
            <body>
                <div class="header">
                    <div class="title">${escapeHtml(gridInfo.title || 'Dashboard')}</div>
                    <div class="file-path">${escapeHtml(fileName)}</div>
                </div>

                <div class="error-banner">
                    <div class="error-banner-title">
                        \u26A0\uFE0F Compilation Error - Layout Edit Mode
                    </div>
                    <div class="error-banner-message">${escapeHtml(errorMessage)}</div>
                    <div class="error-banner-hint">
                        You can still edit the panel layout below. Fix overlapping panels or other layout issues, 
                        then save the file to re-compile.
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">Dashboard Layout</div>
                    <div class="layout-controls">
                        <label class="control-label">
                            <input type="checkbox" id="showGrid" checked> Show Grid Lines
                        </label>
                        <span class="edit-hint">Drag panels to move, drag corners to resize</span>
                    </div>
                    ${layoutHtml}
                </div>

                <!-- Configuration data for external scripts -->
                <script id="layout-config" type="application/json">${layoutConfig}</script>
                
                <!-- External scripts -->
                <script src="${layoutEditorUri}"></script>
            </body>
            </html>
        `;
    }

    private getChartTypeIcon(type: string): string {
        return PreviewPanel.chartTypeRegistry[type.toLowerCase()]?.icon || '\u{1F4C4}';
    }

    private getChartTypeLabel(type: string): string {
        return PreviewPanel.chartTypeRegistry[type.toLowerCase()]?.label || type;
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

        // Calculate the height based on panel positions and generate HTML
        let maxY = 0;
        let panelsHtml = '';

        for (let i = 0; i < gridInfo.panels.length; i++) {
            const panel = gridInfo.panels[i];
            if (!panel.grid ||
                typeof panel.grid.x !== 'number' ||
                typeof panel.grid.y !== 'number' ||
                typeof panel.grid.w !== 'number' ||
                typeof panel.grid.h !== 'number') {
                continue;
            }

            const panelBottom = panel.grid.y + panel.grid.h;
            if (panelBottom > maxY) {
                maxY = panelBottom;
            }

            const left = panel.grid.x * PreviewPanel.scaleFactor;
            const top = panel.grid.y * PreviewPanel.scaleFactor;
            const width = panel.grid.w * PreviewPanel.scaleFactor;
            const height = panel.grid.h * PreviewPanel.scaleFactor;

            panelsHtml += `
                <div class="layout-panel" data-panel-id="${escapeHtml(panel.id)}" data-index="${i}" style="left: ${left}px; top: ${top}px; width: ${width}px; height: ${height}px;" onmousedown="handlePanelMouseDown(event)">
                    <div class="panel-header">${escapeHtml(panel.title || 'Untitled')}</div>
                    <div class="panel-type">Type: ${escapeHtml(panel.type)}</div>
                    <div class="panel-coords">x:${panel.grid.x} y:${panel.grid.y} w:${panel.grid.w} h:${panel.grid.h}</div>
                    <div class="resize-handle" onmousedown="handleResizeMouseDown(event)"></div>
                </div>
            `;
        }

        const containerHeight = (maxY + 10) * PreviewPanel.scaleFactor;
        const containerWidth = PreviewPanel.gridColumns * PreviewPanel.scaleFactor;

        return `
            <div class="layout-container" style="height: ${containerHeight}px; width: ${containerWidth}px;">
                <div class="layout-grid" id="layoutGrid" style="height: ${containerHeight}px; width: ${containerWidth}px;">
                    ${panelsHtml}
                </div>
            </div>
        `;
    }

}
