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

    constructor(
        private compiler: DashboardCompilerLSP,
        private context: vscode.ExtensionContext,
        private configService: ConfigService
    ) {
        this.extensionPath = context.extensionPath;
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
                    retainContextWhenHidden: true
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
        // Cast to any for property access since CompiledDashboard structure is dynamic
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const dashboardData = dashboard as any;
        const fileName = path.basename(filePath);
        // Escape < to prevent </script> injection in embedded JSON
        const ndjson = JSON.stringify(dashboard).replace(/</g, '\\u003c');
        const layoutHtml = this.generateLayoutHtml(gridInfo);
        const jsonFieldsHtml = this.generateJsonFieldsHtml(dashboardData);
        const panelsJson = JSON.stringify(gridInfo.panels).replace(/<\//g, '<\\/');

        return `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    :root {
                        --grid-columns: 48;
                        --cell-size: ${PreviewPanel.scaleFactor}px;
                        --panel-bg: var(--vscode-editor-selectionBackground);
                        --panel-border: var(--vscode-panel-border);
                        --panel-hover: var(--vscode-list-hoverBackground);
                    }

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
                    .stale-warning {
                        background: var(--vscode-inputValidation-warningBackground);
                        border: 1px solid var(--vscode-inputValidation-warningBorder);
                        color: var(--vscode-inputValidation-warningForeground);
                        padding: 10px;
                        border-radius: 3px;
                        margin-top: 10px;
                        display: none;
                        font-size: 12px;
                    }
                    .stale-warning.show {
                        display: block;
                    }

                    /* Layout Preview Styles - Now with drag-and-drop */
                    .layout-controls {
                        margin-bottom: 10px;
                        display: flex;
                        gap: 15px;
                        align-items: center;
                    }
                    .control-label {
                        font-size: 12px;
                        color: var(--vscode-descriptionForeground);
                        display: flex;
                        align-items: center;
                        gap: 5px;
                    }
                    .control-label input[type="checkbox"] {
                        cursor: pointer;
                    }
                    .layout-container {
                        position: relative;
                        width: 100%;
                        background: var(--vscode-textCodeBlock-background);
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 4px;
                        overflow: hidden;
                    }
                    .layout-grid {
                        position: relative;
                        background-image:
                            repeating-linear-gradient(
                                0deg,
                                var(--panel-border) 0px,
                                var(--panel-border) 1px,
                                transparent 1px,
                                transparent var(--cell-size)
                            ),
                            repeating-linear-gradient(
                                90deg,
                                var(--panel-border) 0px,
                                var(--panel-border) 1px,
                                transparent 1px,
                                transparent var(--cell-size)
                            );
                    }
                    .layout-grid.hide-grid {
                        background-image: none;
                    }
                    .layout-panel {
                        position: absolute;
                        background: var(--panel-bg);
                        border: 2px solid var(--panel-border);
                        border-radius: 3px;
                        padding: 8px;
                        box-sizing: border-box;
                        overflow: hidden;
                        display: flex;
                        flex-direction: column;
                        cursor: move;
                        transition: box-shadow 0.2s;
                        user-select: none;
                    }
                    .layout-panel:hover {
                        background: var(--panel-hover);
                        border-color: var(--vscode-focusBorder);
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                    }
                    .layout-panel.dragging {
                        opacity: 0.7;
                        z-index: 1000;
                        cursor: grabbing;
                    }
                    .layout-panel.resizing {
                        opacity: 0.7;
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
                    .panel-size, .panel-coords {
                        font-size: 9px;
                        color: var(--vscode-descriptionForeground);
                        font-family: monospace;
                        margin-top: auto;
                    }
                    .panel-type {
                        font-size: 10px;
                        color: var(--vscode-descriptionForeground);
                        margin-bottom: 4px;
                    }
                    .resize-handle {
                        position: absolute;
                        bottom: 0;
                        right: 0;
                        width: 12px;
                        height: 12px;
                        cursor: se-resize;
                        background: linear-gradient(135deg, transparent 50%, var(--vscode-panel-border) 50%);
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
                    .edit-hint {
                        font-size: 11px;
                        color: var(--vscode-descriptionForeground);
                        font-style: italic;
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

                <script id="ndjson-data" type="application/json">${ndjson}</script>
                <script>
                    // FIRST: Define all globals and handlers before any code that could fail
                    const vscode = acquireVsCodeApi();
                    const GRID_COLUMNS = 48;
                    const CELL_SIZE = ${PreviewPanel.scaleFactor};
                    let panels = [];
                    let ndjsonData = '';
                    let draggedPanel = null;
                    let dragStartX = 0;
                    let dragStartY = 0;
                    let dragStartGridX = 0;
                    let dragStartGridY = 0;
                    let isResizing = false;
                    let resizeStartW = 0;
                    let resizeStartH = 0;

                    // Get DOM elements (may be null if not present)
                    const gridElement = document.getElementById('layoutGrid');
                    const showGridCheckbox = document.getElementById('showGrid');

                    // Define handlers IMMEDIATELY so they're available for inline onmousedown
                    function handlePanelMouseDown(e) {
                        if (e.target.classList.contains('resize-handle')) {
                            return;
                        }
                        e.preventDefault();
                        draggedPanel = e.target.closest('.layout-panel');
                        if (!draggedPanel) return;
                        
                        const index = parseInt(draggedPanel.dataset.index, 10);
                        if (isNaN(index) || !panels[index]) return;
                        
                        dragStartX = e.clientX;
                        dragStartY = e.clientY;
                        dragStartGridX = panels[index].grid.x;
                        dragStartGridY = panels[index].grid.y;
                        isResizing = false;

                        draggedPanel.classList.add('dragging');

                        document.addEventListener('mousemove', handleMouseMove);
                        document.addEventListener('mouseup', handleMouseUp);
                    }

                    function handleResizeMouseDown(e) {
                        e.preventDefault();
                        e.stopPropagation();

                        isResizing = true;
                        draggedPanel = e.target.closest('.layout-panel');
                        if (!draggedPanel) return;
                        
                        const index = parseInt(draggedPanel.dataset.index, 10);
                        if (isNaN(index) || !panels[index]) return;

                        dragStartX = e.clientX;
                        dragStartY = e.clientY;
                        resizeStartW = panels[index].grid.w;
                        resizeStartH = panels[index].grid.h;

                        draggedPanel.classList.add('resizing');

                        document.addEventListener('mousemove', handleMouseMove);
                        document.addEventListener('mouseup', handleMouseUp);
                    }

                    function handleMouseMove(e) {
                        if (!draggedPanel) return;

                        const index = parseInt(draggedPanel.dataset.index, 10);
                        if (isNaN(index) || !panels[index]) return;
                        const panel = panels[index];

                        if (isResizing) {
                            const deltaX = e.clientX - dragStartX;
                            const deltaY = e.clientY - dragStartY;

                            let newW = resizeStartW + Math.round(deltaX / CELL_SIZE);
                            let newH = resizeStartH + Math.round(deltaY / CELL_SIZE);

                            newW = Math.max(4, newW);
                            newH = Math.max(4, newH);
                            newW = Math.min(newW, GRID_COLUMNS - panel.grid.x);

                            panel.grid.w = newW;
                            panel.grid.h = newH;

                            draggedPanel.style.width = (newW * CELL_SIZE) + 'px';
                            draggedPanel.style.height = (newH * CELL_SIZE) + 'px';

                            const coordsElement = draggedPanel.querySelector('.panel-coords');
                            if (coordsElement) coordsElement.textContent = 'x:' + panel.grid.x + ' y:' + panel.grid.y + ' w:' + panel.grid.w + ' h:' + panel.grid.h;
                        } else {
                            const deltaX = e.clientX - dragStartX;
                            const deltaY = e.clientY - dragStartY;

                            let newX = dragStartGridX + Math.round(deltaX / CELL_SIZE);
                            let newY = dragStartGridY + Math.round(deltaY / CELL_SIZE);

                            newX = Math.max(0, Math.min(newX, GRID_COLUMNS - panel.grid.w));
                            newY = Math.max(0, newY);

                            panel.grid.x = newX;
                            panel.grid.y = newY;

                            draggedPanel.style.left = (newX * CELL_SIZE) + 'px';
                            draggedPanel.style.top = (newY * CELL_SIZE) + 'px';

                            const coordsElement = draggedPanel.querySelector('.panel-coords');
                            if (coordsElement) coordsElement.textContent = 'x:' + panel.grid.x + ' y:' + panel.grid.y + ' w:' + panel.grid.w + ' h:' + panel.grid.h;
                        }
                    }

                    function handleMouseUp() {
                        if (!draggedPanel) return;

                        const index = parseInt(draggedPanel.dataset.index, 10);
                        if (isNaN(index) || !panels[index]) {
                            draggedPanel.classList.remove('dragging', 'resizing');
                            draggedPanel = null;
                            isResizing = false;
                            document.removeEventListener('mousemove', handleMouseMove);
                            document.removeEventListener('mouseup', handleMouseUp);
                            return;
                        }
                        const panel = panels[index];

                        vscode.postMessage({
                            command: 'updateGrid',
                            panelId: panel.id,
                            grid: panel.grid
                        });

                        // Show stale warning since NDJSON output won't reflect the new layout
                        const staleWarning = document.getElementById('staleWarning');
                        if (staleWarning) {
                            staleWarning.classList.add('show');
                        }

                        draggedPanel.classList.remove('dragging', 'resizing');
                        draggedPanel = null;
                        isResizing = false;

                        document.removeEventListener('mousemove', handleMouseMove);
                        document.removeEventListener('mouseup', handleMouseUp);
                    }

                    function escapeHtmlClient(text) {
                        const div = document.createElement('div');
                        div.textContent = text;
                        return div.innerHTML;
                    }

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
                            if (message) {
                                message.classList.add('show');
                                setTimeout(() => { message.classList.remove('show'); }, 3000);
                            }
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

                    function calculateGridHeight() {
                        let maxY = 20;
                        panels.forEach(panel => {
                            const panelBottom = panel.grid.y + panel.grid.h;
                            if (panelBottom > maxY) {
                                maxY = panelBottom;
                            }
                        });
                        return maxY + 10;
                    }

                    // NOW initialize data (this can fail without breaking handlers)
                    // Keep as string for clipboard/download - don't parse to object
                    try {
                        ndjsonData = document.getElementById('ndjson-data')?.textContent ?? '';
                    } catch (e) {
                        console.error('Failed to read ndjson data:', e);
                        ndjsonData = '';
                    }

                    try {
                        panels = ${panelsJson};
                    } catch (e) {
                        console.error('Failed to parse panels:', e);
                        panels = [];
                    }

                    // Set up grid height and checkbox listeners
                    if (gridElement && panels.length > 0) {
                        const gridHeight = calculateGridHeight();
                        gridElement.style.height = (gridHeight * CELL_SIZE) + 'px';
                    }

                    if (showGridCheckbox) {
                        showGridCheckbox.addEventListener('change', (e) => {
                            if (gridElement) {
                                if (e.target.checked) {
                                    gridElement.classList.remove('hide-grid');
                                } else {
                                    gridElement.classList.add('hide-grid');
                                }
                            }
                        });
                    }
                </script>
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
        const fileName = path.basename(filePath);
        const layoutHtml = this.generateLayoutHtml(gridInfo);
        const panelsJson = JSON.stringify(gridInfo.panels).replace(/<\//g, '<\\/');

        return `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    :root {
                        --grid-columns: 48;
                        --cell-size: ${PreviewPanel.scaleFactor}px;
                        --panel-bg: var(--vscode-editor-selectionBackground);
                        --panel-border: var(--vscode-panel-border);
                        --panel-hover: var(--vscode-list-hoverBackground);
                    }

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
                    .error-banner {
                        background: var(--vscode-inputValidation-errorBackground);
                        border: 1px solid var(--vscode-inputValidation-errorBorder);
                        color: var(--vscode-inputValidation-errorForeground);
                        padding: 12px 16px;
                        border-radius: 4px;
                        margin-bottom: 20px;
                    }
                    .error-banner-title {
                        font-weight: bold;
                        margin-bottom: 8px;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }
                    .error-banner-message {
                        font-size: 12px;
                        white-space: pre-wrap;
                        font-family: var(--vscode-editor-font-family);
                        max-height: 150px;
                        overflow-y: auto;
                    }
                    .error-banner-hint {
                        margin-top: 10px;
                        font-size: 12px;
                        font-style: italic;
                        opacity: 0.9;
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
                    .layout-container {
                        position: relative;
                        background: var(--vscode-editor-background);
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 4px;
                        overflow: auto;
                        max-height: 600px;
                    }
                    .layout-grid {
                        position: relative;
                        background-image: 
                            linear-gradient(to right, var(--vscode-panel-border) 1px, transparent 1px),
                            linear-gradient(to bottom, var(--vscode-panel-border) 1px, transparent 1px);
                        background-size: calc(var(--cell-size) * 4) calc(var(--cell-size) * 4);
                        width: calc(var(--cell-size) * var(--grid-columns));
                        min-height: 400px;
                    }
                    .layout-grid.hide-grid {
                        background-image: none;
                    }
                    .layout-panel {
                        position: absolute;
                        background: var(--panel-bg);
                        border: 2px solid var(--panel-border);
                        border-radius: 4px;
                        padding: 8px;
                        box-sizing: border-box;
                        cursor: grab;
                        overflow: hidden;
                        transition: box-shadow 0.15s;
                    }
                    .layout-panel:hover {
                        border-color: var(--vscode-focusBorder);
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                    }
                    .layout-panel.dragging {
                        cursor: grabbing;
                        opacity: 0.8;
                        border-color: var(--vscode-focusBorder);
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
                        z-index: 1000;
                    }
                    .layout-panel.resizing {
                        cursor: se-resize;
                        opacity: 0.9;
                        border-color: var(--vscode-focusBorder);
                    }
                    .panel-header {
                        font-weight: bold;
                        font-size: 11px;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        margin-bottom: 4px;
                    }
                    .panel-type {
                        font-size: 10px;
                        color: var(--vscode-descriptionForeground);
                        margin-bottom: 2px;
                    }
                    .panel-coords {
                        font-size: 9px;
                        color: var(--vscode-descriptionForeground);
                        font-family: var(--vscode-editor-font-family);
                    }
                    .resize-handle {
                        position: absolute;
                        bottom: 0;
                        right: 0;
                        width: 16px;
                        height: 16px;
                        cursor: se-resize;
                        background: linear-gradient(135deg, transparent 50%, var(--vscode-focusBorder) 50%);
                        opacity: 0.5;
                        border-radius: 0 0 2px 0;
                    }
                    .resize-handle:hover {
                        opacity: 1;
                    }
                    .layout-controls {
                        display: flex;
                        gap: 20px;
                        margin-bottom: 10px;
                        align-items: center;
                    }
                    .control-label {
                        display: flex;
                        align-items: center;
                        gap: 6px;
                        font-size: 12px;
                        cursor: pointer;
                    }
                    .control-label input[type="checkbox"] {
                        cursor: pointer;
                    }
                    .edit-hint {
                        font-size: 11px;
                        color: var(--vscode-descriptionForeground);
                        font-style: italic;
                    }
                </style>
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

                <script>
                    // FIRST: Define all globals and handlers before any code that could fail
                    const vscode = acquireVsCodeApi();
                    const GRID_COLUMNS = 48;
                    const CELL_SIZE = ${PreviewPanel.scaleFactor};
                    let panels = [];
                    let draggedPanel = null;
                    let dragStartX = 0;
                    let dragStartY = 0;
                    let dragStartGridX = 0;
                    let dragStartGridY = 0;
                    let isResizing = false;
                    let resizeStartW = 0;
                    let resizeStartH = 0;

                    const gridElement = document.getElementById('layoutGrid');
                    const showGridCheckbox = document.getElementById('showGrid');

                    function handlePanelMouseDown(e) {
                        if (e.target.classList.contains('resize-handle')) {
                            return;
                        }
                        e.preventDefault();
                        draggedPanel = e.target.closest('.layout-panel');
                        if (!draggedPanel) return;
                        
                        const index = parseInt(draggedPanel.dataset.index, 10);
                        if (isNaN(index) || !panels[index]) return;
                        
                        dragStartX = e.clientX;
                        dragStartY = e.clientY;
                        dragStartGridX = panels[index].grid.x;
                        dragStartGridY = panels[index].grid.y;
                        isResizing = false;

                        draggedPanel.classList.add('dragging');

                        document.addEventListener('mousemove', handleMouseMove);
                        document.addEventListener('mouseup', handleMouseUp);
                    }

                    function handleResizeMouseDown(e) {
                        e.preventDefault();
                        e.stopPropagation();

                        isResizing = true;
                        draggedPanel = e.target.closest('.layout-panel');
                        if (!draggedPanel) return;
                        
                        const index = parseInt(draggedPanel.dataset.index, 10);
                        if (isNaN(index) || !panels[index]) return;

                        dragStartX = e.clientX;
                        dragStartY = e.clientY;
                        resizeStartW = panels[index].grid.w;
                        resizeStartH = panels[index].grid.h;

                        draggedPanel.classList.add('resizing');

                        document.addEventListener('mousemove', handleMouseMove);
                        document.addEventListener('mouseup', handleMouseUp);
                    }

                    function handleMouseMove(e) {
                        if (!draggedPanel) return;

                        const index = parseInt(draggedPanel.dataset.index, 10);
                        if (isNaN(index) || !panels[index]) return;
                        const panel = panels[index];

                        if (isResizing) {
                            const deltaX = e.clientX - dragStartX;
                            const deltaY = e.clientY - dragStartY;

                            let newW = resizeStartW + Math.round(deltaX / CELL_SIZE);
                            let newH = resizeStartH + Math.round(deltaY / CELL_SIZE);

                            newW = Math.max(4, newW);
                            newH = Math.max(4, newH);
                            newW = Math.min(newW, GRID_COLUMNS - panel.grid.x);

                            panel.grid.w = newW;
                            panel.grid.h = newH;

                            draggedPanel.style.width = (newW * CELL_SIZE) + 'px';
                            draggedPanel.style.height = (newH * CELL_SIZE) + 'px';

                            const coordsElement = draggedPanel.querySelector('.panel-coords');
                            if (coordsElement) coordsElement.textContent = 'x:' + panel.grid.x + ' y:' + panel.grid.y + ' w:' + panel.grid.w + ' h:' + panel.grid.h;
                        } else {
                            const deltaX = e.clientX - dragStartX;
                            const deltaY = e.clientY - dragStartY;

                            let newX = dragStartGridX + Math.round(deltaX / CELL_SIZE);
                            let newY = dragStartGridY + Math.round(deltaY / CELL_SIZE);

                            newX = Math.max(0, Math.min(newX, GRID_COLUMNS - panel.grid.w));
                            newY = Math.max(0, newY);

                            panel.grid.x = newX;
                            panel.grid.y = newY;

                            draggedPanel.style.left = (newX * CELL_SIZE) + 'px';
                            draggedPanel.style.top = (newY * CELL_SIZE) + 'px';

                            const coordsElement = draggedPanel.querySelector('.panel-coords');
                            if (coordsElement) coordsElement.textContent = 'x:' + panel.grid.x + ' y:' + panel.grid.y + ' w:' + panel.grid.w + ' h:' + panel.grid.h;
                        }
                    }

                    function handleMouseUp() {
                        if (!draggedPanel) return;

                        const index = parseInt(draggedPanel.dataset.index, 10);
                        if (isNaN(index) || !panels[index]) {
                            draggedPanel.classList.remove('dragging', 'resizing');
                            draggedPanel = null;
                            isResizing = false;
                            document.removeEventListener('mousemove', handleMouseMove);
                            document.removeEventListener('mouseup', handleMouseUp);
                            return;
                        }
                        const panel = panels[index];

                        vscode.postMessage({
                            command: 'updateGrid',
                            panelId: panel.id,
                            grid: panel.grid
                        });

                        draggedPanel.classList.remove('dragging', 'resizing');
                        draggedPanel = null;
                        isResizing = false;

                        document.removeEventListener('mousemove', handleMouseMove);
                        document.removeEventListener('mouseup', handleMouseUp);
                    }

                    function calculateGridHeight() {
                        let maxY = 20;
                        panels.forEach(panel => {
                            const panelBottom = panel.grid.y + panel.grid.h;
                            if (panelBottom > maxY) {
                                maxY = panelBottom;
                            }
                        });
                        return maxY + 10;
                    }

                    // Initialize panels data
                    try {
                        panels = ${panelsJson};
                    } catch (e) {
                        console.error('Failed to parse panels:', e);
                        panels = [];
                    }

                    // Set up grid height and checkbox listeners
                    if (gridElement && panels.length > 0) {
                        const gridHeight = calculateGridHeight();
                        gridElement.style.height = (gridHeight * CELL_SIZE) + 'px';
                    }

                    if (showGridCheckbox) {
                        showGridCheckbox.addEventListener('change', (e) => {
                            if (gridElement) {
                                if (e.target.checked) {
                                    gridElement.classList.remove('hide-grid');
                                } else {
                                    gridElement.classList.add('hide-grid');
                                }
                            }
                        });
                    }
                </script>
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
