import * as vscode from 'vscode';
import * as path from 'path';
import { spawn } from 'child_process';
import { escapeHtml, getLoadingContent, getErrorContent } from './webviewUtils';
import { ConfigService } from './configService';
import { BinaryResolver } from './binaryResolver';

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

export class GridEditorPanel {
    private panel: vscode.WebviewPanel | undefined;
    private currentDashboardPath: string | undefined;
    private currentDashboardIndex: number = 0;
    private extensionPath: string;

    constructor(
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
        if (!this.isPathInWorkspace(dashboardPath)) {
            vscode.window.showErrorMessage('Dashboard file must be within the workspace');
            return;
        }

        this.currentDashboardPath = dashboardPath;
        this.currentDashboardIndex = dashboardIndex;

        if (!this.panel) {
            this.panel = vscode.window.createWebviewPanel(
                'dashboardGridEditor',
                'Dashboard Grid Editor',
                vscode.ViewColumn.Beside,
                {
                    enableScripts: true,
                    retainContextWhenHidden: true
                }
            );

            this.panel.onDidDispose(() => {
                this.panel = undefined;
            });

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

        await this.loadAndDisplayGrid(dashboardPath, dashboardIndex);
    }

    private async loadAndDisplayGrid(dashboardPath: string, dashboardIndex: number = 0) {
        if (!this.panel) {
            return;
        }

        this.panel.webview.html = getLoadingContent('Loading grid editor...');

        try {
            const gridInfo = await this.extractGridInfo(dashboardPath, dashboardIndex);
            this.panel.webview.html = this.getGridEditorContent(gridInfo, dashboardPath);
        } catch (error) {
            this.panel.webview.html = getErrorContent(error, 'Grid Editor Error');
        }
    }

    private async runPythonScript<T = unknown>(
        args: string[],
        errorContext: string,
        parseResult: (stdout: string) => T,
        timeout: number = 30000
    ): Promise<T> {
        const resolver = new BinaryResolver(this.extensionPath, this.configService);
        const pythonPath = resolver.resolvePythonForScripts();

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

            const child = spawn(pythonPath, args, {
                cwd: path.join(this.extensionPath, '..')
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

    private async updatePanelGrid(panelId: string, grid: { x: number; y: number; w: number; h: number }): Promise<string | undefined> {
        if (!this.currentDashboardPath) {
            return;
        }

        try {
            return await this.runPythonScript(
                ['-m', 'dashboard_compiler.lsp.grid_updater', this.currentDashboardPath, panelId, JSON.stringify(grid), this.currentDashboardIndex.toString()],
                'Grid update',
                (stdout) => stdout
            );
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to update grid: ${error instanceof Error ? error.message : String(error)}`);
            return;
        }
    }

    private isPathInWorkspace(filePath: string): boolean {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            return false;
        }

        const normalizedPath = path.resolve(filePath);
        for (const folder of workspaceFolders) {
            const folderPath = path.resolve(folder.uri.fsPath);
            if (normalizedPath.startsWith(folderPath)) {
                return true;
            }
        }

        return false;
    }

    private getGridEditorContent(gridInfo: DashboardGridInfo, filePath: string): string {
        const fileName = path.basename(filePath);
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
                        --cell-size: 20px;
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
                        overflow: auto;
                    }

                    .header {
                        border-bottom: 1px solid var(--vscode-panel-border);
                        padding-bottom: 20px;
                        margin-bottom: 20px;
                    }

                    .title {
                        font-size: 24px;
                        font-weight: bold;
                        margin-bottom: 5px;
                    }

                    .subtitle {
                        color: var(--vscode-descriptionForeground);
                        font-size: 14px;
                        margin-bottom: 10px;
                    }

                    .file-path {
                        color: var(--vscode-descriptionForeground);
                        font-size: 12px;
                        margin-bottom: 15px;
                    }

                    .info-message {
                        background: var(--vscode-inputValidation-infoBackground);
                        border: 1px solid var(--vscode-inputValidation-infoBorder);
                        color: var(--vscode-inputValidation-infoForeground);
                        padding: 10px;
                        border-radius: 3px;
                        margin-bottom: 15px;
                        font-size: 12px;
                    }

                    .controls {
                        margin-bottom: 20px;
                        display: flex;
                        gap: 10px;
                        align-items: center;
                    }

                    .control-label {
                        font-size: 12px;
                        color: var(--vscode-descriptionForeground);
                    }

                    input[type="checkbox"] {
                        cursor: pointer;
                    }

                    .grid-container {
                        position: relative;
                        display: inline-block;
                        background: var(--vscode-editor-background);
                        border: 1px solid var(--panel-border);
                        padding: 10px;
                    }

                    .grid {
                        display: grid;
                        grid-template-columns: repeat(var(--grid-columns), var(--cell-size));
                        gap: 0;
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

                    .grid.hide-grid {
                        background-image: none;
                    }

                    .panel {
                        position: absolute;
                        background: var(--panel-bg);
                        border: 2px solid var(--panel-border);
                        border-radius: 4px;
                        cursor: move;
                        padding: 8px;
                        box-sizing: border-box;
                        overflow: hidden;
                        display: flex;
                        flex-direction: column;
                        transition: box-shadow 0.2s;
                    }

                    .panel:hover {
                        background: var(--panel-hover);
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                    }

                    .panel.dragging {
                        opacity: 0.7;
                        z-index: 1000;
                    }

                    .panel.resizing {
                        opacity: 0.7;
                    }

                    .panel-header {
                        font-weight: bold;
                        font-size: 12px;
                        margin-bottom: 4px;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    }

                    .panel-type {
                        font-size: 10px;
                        color: var(--vscode-descriptionForeground);
                        margin-bottom: 4px;
                    }

                    .panel-coords {
                        font-size: 9px;
                        color: var(--vscode-descriptionForeground);
                        font-family: monospace;
                        margin-top: auto;
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

                    .legend {
                        margin-top: 20px;
                        padding: 15px;
                        background: var(--vscode-textCodeBlock-background);
                        border: 1px solid var(--panel-border);
                        border-radius: 3px;
                    }

                    .legend h3 {
                        margin-top: 0;
                        font-size: 14px;
                    }

                    .legend ul {
                        margin: 5px 0;
                        padding-left: 20px;
                        font-size: 12px;
                    }

                    .legend li {
                        margin: 3px 0;
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="title">${escapeHtml(gridInfo.title)}</div>
                    <div class="subtitle">Grid Layout Editor</div>
                    <div class="file-path">${escapeHtml(fileName)}</div>
                    <div class="info-message">
                        Drag panels to move them, drag the bottom-right corner to resize. Changes are saved automatically to the YAML file.
                    </div>
                    <div class="controls">
                        <label class="control-label">
                            <input type="checkbox" id="showGrid" checked> Show Grid Lines
                        </label>
                        <label class="control-label">
                            <input type="checkbox" id="snapToGrid" checked> Snap to Grid (4 units)
                        </label>
                    </div>
                </div>

                <div class="grid-container">
                    <div class="grid" id="grid"></div>
                </div>

                <div class="legend">
                    <h3>How to Use</h3>
                    <ul>
                        <li><strong>Move:</strong> Click and drag a panel to move it</li>
                        <li><strong>Resize:</strong> Drag the bottom-right corner of a panel</li>
                        <li><strong>Grid:</strong> Kibana uses a 48-column grid (full width = 48 units)</li>
                        <li><strong>Snap:</strong> Panels snap to 4-unit increments for alignment</li>
                    </ul>
                </div>

                <script>
                    const vscode = acquireVsCodeApi();
                    const panels = ${panelsJson};
                    const GRID_COLUMNS = 48;
                    const CELL_SIZE = 20;
                    const SNAP_UNITS = 4;

                    let draggedPanel = null;
                    let dragStartX = 0;
                    let dragStartY = 0;
                    let dragStartGridX = 0;
                    let dragStartGridY = 0;
                    let isResizing = false;
                    let resizeStartW = 0;
                    let resizeStartH = 0;

                    /**
                     * Client-side HTML escape function to prevent XSS
                     */
                    function escapeHtml(text) {
                        const div = document.createElement('div');
                        div.textContent = text;
                        return div.innerHTML;
                    }

                    const gridElement = document.getElementById('grid');
                    const showGridCheckbox = document.getElementById('showGrid');
                    const snapToGridCheckbox = document.getElementById('snapToGrid');

                    // Calculate grid height based on panels
                    function calculateGridHeight() {
                        let maxY = 20;
                        panels.forEach(panel => {
                            const panelBottom = panel.grid.y + panel.grid.h;
                            if (panelBottom > maxY) {
                                maxY = panelBottom;
                            }
                        });
                        return maxY + 10; // Add some padding
                    }

                    const gridHeight = calculateGridHeight();
                    gridElement.style.height = (gridHeight * CELL_SIZE) + 'px';

                    // Toggle grid lines
                    showGridCheckbox.addEventListener('change', (e) => {
                        if (e.target.checked) {
                            gridElement.classList.remove('hide-grid');
                        } else {
                            gridElement.classList.add('hide-grid');
                        }
                    });

                    // Render panels
                    function renderPanels() {
                        gridElement.innerHTML = '';
                        panels.forEach((panel, index) => {
                            const panelElement = document.createElement('div');
                            panelElement.className = 'panel';
                            panelElement.dataset.panelId = panel.id;
                            panelElement.dataset.index = index;

                            const left = panel.grid.x * CELL_SIZE;
                            const top = panel.grid.y * CELL_SIZE;
                            const width = panel.grid.w * CELL_SIZE;
                            const height = panel.grid.h * CELL_SIZE;

                            panelElement.style.left = left + 'px';
                            panelElement.style.top = top + 'px';
                            panelElement.style.width = width + 'px';
                            panelElement.style.height = height + 'px';

                            panelElement.innerHTML = \`
                                <div class="panel-header">\${escapeHtml(panel.title || 'Untitled')}</div>
                                <div class="panel-type">Type: \${escapeHtml(panel.type)}</div>
                                <div class="panel-coords">
                                    x:\${panel.grid.x} y:\${panel.grid.y} w:\${panel.grid.w} h:\${panel.grid.h}
                                </div>
                                <div class="resize-handle"></div>
                            \`;

                            // Add drag listeners to panel
                            panelElement.addEventListener('mousedown', handlePanelMouseDown);

                            // Add resize listeners to resize handle
                            const resizeHandle = panelElement.querySelector('.resize-handle');
                            resizeHandle.addEventListener('mousedown', handleResizeMouseDown);

                            gridElement.appendChild(panelElement);
                        });
                    }

                    function handlePanelMouseDown(e) {
                        // Don't start drag if clicking on resize handle
                        if (e.target.classList.contains('resize-handle')) {
                            return;
                        }

                        e.preventDefault();
                        draggedPanel = e.currentTarget;
                        const index = parseInt(draggedPanel.dataset.index, 10);
                        dragStartX = e.clientX;
                        dragStartY = e.clientY;
                        dragStartGridX = panels[index].grid.x;
                        dragStartGridY = panels[index].grid.y;

                        draggedPanel.classList.add('dragging');

                        document.addEventListener('mousemove', handleMouseMove);
                        document.addEventListener('mouseup', handleMouseUp);
                    }

                    function handleResizeMouseDown(e) {
                        e.preventDefault();
                        e.stopPropagation();

                        isResizing = true;
                        draggedPanel = e.target.closest('.panel');
                        const index = parseInt(draggedPanel.dataset.index, 10);

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
                        const panel = panels[index];

                        if (isResizing) {
                            // Handle resizing
                            const deltaX = e.clientX - dragStartX;
                            const deltaY = e.clientY - dragStartY;

                            let newW = resizeStartW + Math.round(deltaX / CELL_SIZE);
                            let newH = resizeStartH + Math.round(deltaY / CELL_SIZE);

                            // Apply snap to grid
                            if (snapToGridCheckbox.checked) {
                                newW = Math.round(newW / SNAP_UNITS) * SNAP_UNITS;
                                newH = Math.round(newH / SNAP_UNITS) * SNAP_UNITS;
                            }

                            // Minimum size
                            newW = Math.max(4, newW);
                            newH = Math.max(4, newH);

                            // Don't exceed grid width
                            newW = Math.min(newW, GRID_COLUMNS - panel.grid.x);

                            panel.grid.w = newW;
                            panel.grid.h = newH;

                            // Update visual
                            draggedPanel.style.width = (newW * CELL_SIZE) + 'px';
                            draggedPanel.style.height = (newH * CELL_SIZE) + 'px';

                            // Update coords display
                            const coordsElement = draggedPanel.querySelector('.panel-coords');
                            coordsElement.textContent = \`x:\${panel.grid.x} y:\${panel.grid.y} w:\${panel.grid.w} h:\${panel.grid.h}\`;
                        } else {
                            // Handle dragging
                            const deltaX = e.clientX - dragStartX;
                            const deltaY = e.clientY - dragStartY;

                            let newX = dragStartGridX + Math.round(deltaX / CELL_SIZE);
                            let newY = dragStartGridY + Math.round(deltaY / CELL_SIZE);

                            // Apply snap to grid
                            if (snapToGridCheckbox.checked) {
                                newX = Math.round(newX / SNAP_UNITS) * SNAP_UNITS;
                                newY = Math.round(newY / SNAP_UNITS) * SNAP_UNITS;
                            }

                            // Constrain to grid bounds
                            newX = Math.max(0, Math.min(newX, GRID_COLUMNS - panel.grid.w));
                            newY = Math.max(0, newY);

                            panel.grid.x = newX;
                            panel.grid.y = newY;

                            // Update visual
                            draggedPanel.style.left = (newX * CELL_SIZE) + 'px';
                            draggedPanel.style.top = (newY * CELL_SIZE) + 'px';

                            // Update coords display
                            const coordsElement = draggedPanel.querySelector('.panel-coords');
                            coordsElement.textContent = \`x:\${panel.grid.x} y:\${panel.grid.y} w:\${panel.grid.w} h:\${panel.grid.h}\`;
                        }
                    }

                    function handleMouseUp() {
                        if (!draggedPanel) return;

                        const index = parseInt(draggedPanel.dataset.index, 10);
                        const panel = panels[index];

                        // Send update to extension
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

                    // Initial render
                    renderPanels();
                </script>
            </body>
            </html>
        `;
    }

}
