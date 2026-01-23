import * as vscode from 'vscode';
import { EsqlQueryResult, EsqlColumn } from './compiler';
import { escapeHtml, getLoadingContent, getErrorContent } from './webviewUtils';

export class EsqlResultsPanel {
    private panel: vscode.WebviewPanel | undefined;

    dispose(): void {
        if (this.panel) {
            this.panel.dispose();
            this.panel = undefined;
        }
    }

    /**
     * Gets or creates the webview panel, handling lifecycle properly.
     * If panel exists, reveals it; otherwise creates a new one.
     */
    private ensurePanel(): vscode.WebviewPanel {
        if (!this.panel) {
            this.panel = vscode.window.createWebviewPanel(
                'esqlResults',
                'ES|QL Results',
                vscode.ViewColumn.Beside,
                {
                    enableScripts: true,
                    retainContextWhenHidden: true
                }
            );

            this.panel.onDidDispose(() => {
                this.panel = undefined;
            });
        } else {
            this.panel.reveal(vscode.ViewColumn.Beside, true);
        }
        return this.panel;
    }

    showLoading(query: string): void {
        const panel = this.ensurePanel();
        panel.title = `ES|QL: ${this.truncateQuery(query)}`;
        panel.webview.html = getLoadingContent('Executing ES|QL query...');
    }

    showResults(result: EsqlQueryResult, query: string): void {
        const panel = this.ensurePanel();
        panel.title = `ES|QL: ${this.truncateQuery(query)}`;
        panel.webview.html = this.getWebviewContent(result, query);
    }

    showError(error: unknown, query: string): void {
        const panel = this.ensurePanel();
        panel.title = `ES|QL Error: ${this.truncateQuery(query)}`;
        panel.webview.html = getErrorContent(error, 'ES|QL Query Error');
    }

    /**
     * Truncate a query string for display in the panel title.
     */
    private truncateQuery(query: string): string {
        const firstLine = query.split('\n')[0].trim();
        const maxLength = 30;
        if (firstLine.length <= maxLength) {
            return firstLine;
        }
        return firstLine.substring(0, maxLength) + '...';
    }

    private getWebviewContent(result: EsqlQueryResult, query: string): string {
        const rowCount = result.values.length;
        const columnCount = result.columns.length;
        const tookMs = result.took !== undefined ? `${result.took}ms` : 'N/A';
        const isPartial = result.is_partial ? ' (partial results)' : '';

        const tableHtml = this.generateTableHtml(result.columns, result.values);

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
                        padding-bottom: 15px;
                        margin-bottom: 15px;
                    }
                    .title {
                        font-size: 20px;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }
                    .metadata {
                        display: flex;
                        gap: 20px;
                        flex-wrap: wrap;
                        margin-bottom: 10px;
                    }
                    .metadata-item {
                        display: flex;
                        align-items: center;
                        gap: 6px;
                    }
                    .metadata-label {
                        color: var(--vscode-descriptionForeground);
                        font-size: 12px;
                    }
                    .metadata-value {
                        font-weight: 600;
                        font-size: 12px;
                    }
                    .query-section {
                        margin-bottom: 15px;
                    }
                    .query-toggle {
                        cursor: pointer;
                        user-select: none;
                        padding: 8px 12px;
                        background: var(--vscode-editor-selectionBackground);
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 3px;
                        display: inline-flex;
                        align-items: center;
                        gap: 8px;
                        font-size: 12px;
                    }
                    .query-toggle:hover {
                        background: var(--vscode-list-hoverBackground);
                    }
                    .query-arrow {
                        font-size: 10px;
                        transition: transform 0.2s;
                    }
                    .query-arrow.expanded {
                        transform: rotate(90deg);
                    }
                    .query-content {
                        display: none;
                        margin-top: 10px;
                    }
                    .query-content.expanded {
                        display: block;
                    }
                    .query-content pre {
                        background: var(--vscode-textCodeBlock-background);
                        padding: 12px;
                        border-radius: 3px;
                        border: 1px solid var(--vscode-panel-border);
                        overflow-x: auto;
                        margin: 0;
                        font-family: var(--vscode-editor-font-family);
                        font-size: var(--vscode-editor-font-size);
                        white-space: pre-wrap;
                        word-wrap: break-word;
                    }
                    .results-section {
                        overflow: auto;
                    }
                    .results-table {
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 13px;
                    }
                    .results-table th {
                        position: sticky;
                        top: 0;
                        background: var(--vscode-editor-selectionBackground);
                        border: 1px solid var(--vscode-panel-border);
                        padding: 8px 12px;
                        text-align: left;
                        font-weight: 600;
                        white-space: nowrap;
                    }
                    .results-table th .col-type {
                        font-weight: normal;
                        color: var(--vscode-descriptionForeground);
                        font-size: 10px;
                        display: block;
                    }
                    .results-table td {
                        border: 1px solid var(--vscode-panel-border);
                        padding: 6px 12px;
                        vertical-align: top;
                    }
                    .results-table tr:nth-child(even) {
                        background: var(--vscode-editor-selectionBackground);
                    }
                    .results-table tr:hover {
                        background: var(--vscode-list-hoverBackground);
                    }
                    .cell-null {
                        color: var(--vscode-descriptionForeground);
                        font-style: italic;
                    }
                    .cell-number {
                        font-family: var(--vscode-editor-font-family);
                    }
                    .cell-boolean {
                        font-weight: 600;
                    }
                    .cell-boolean.true {
                        color: var(--vscode-charts-green);
                    }
                    .cell-boolean.false {
                        color: var(--vscode-charts-red);
                    }
                    .no-results {
                        text-align: center;
                        padding: 40px;
                        color: var(--vscode-descriptionForeground);
                    }
                    .export-btn {
                        background: var(--vscode-button-background);
                        color: var(--vscode-button-foreground);
                        border: none;
                        padding: 6px 12px;
                        cursor: pointer;
                        border-radius: 2px;
                        font-family: var(--vscode-font-family);
                        font-size: 12px;
                    }
                    .export-btn:hover {
                        background: var(--vscode-button-hoverBackground);
                    }
                    .actions {
                        display: flex;
                        gap: 8px;
                        margin-top: 10px;
                    }
                    .success-message {
                        background: var(--vscode-inputValidation-infoBackground);
                        border: 1px solid var(--vscode-inputValidation-infoBorder);
                        color: var(--vscode-inputValidation-infoForeground);
                        padding: 8px 12px;
                        border-radius: 3px;
                        margin-top: 10px;
                        display: none;
                        font-size: 12px;
                    }
                    .success-message.show {
                        display: block;
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="title">ES|QL Query Results${escapeHtml(isPartial)}</div>
                    <div class="metadata">
                        <div class="metadata-item">
                            <span class="metadata-label">Rows:</span>
                            <span class="metadata-value">${rowCount}</span>
                        </div>
                        <div class="metadata-item">
                            <span class="metadata-label">Columns:</span>
                            <span class="metadata-value">${columnCount}</span>
                        </div>
                        <div class="metadata-item">
                            <span class="metadata-label">Time:</span>
                            <span class="metadata-value">${escapeHtml(tookMs)}</span>
                        </div>
                    </div>
                    <div class="actions">
                        <button class="export-btn" onclick="copyAsCsv()">Copy as CSV</button>
                        <button class="export-btn" onclick="copyAsJson()">Copy as JSON</button>
                    </div>
                    <div class="success-message" id="successMessage">Copied to clipboard!</div>
                </div>

                <div class="query-section">
                    <div class="query-toggle" onclick="toggleQuery()">
                        <span class="query-arrow" id="query-arrow">&#9654;</span>
                        <span>Show Query</span>
                    </div>
                    <div class="query-content" id="query-content">
                        <pre>${escapeHtml(query)}</pre>
                    </div>
                </div>

                <div class="results-section">
                    ${tableHtml}
                </div>

                <script id="results-data" type="application/json">${JSON.stringify({ columns: result.columns, values: result.values }).replace(/</g, '\\u003c')}</script>
                <script>
                    let resultsData;
                    try {
                        resultsData = JSON.parse(document.getElementById('results-data').textContent);
                    } catch (e) {
                        console.error('Failed to parse results data:', e);
                        resultsData = { columns: [], values: [] };
                    }

                    function toggleQuery() {
                        const content = document.getElementById('query-content');
                        const arrow = document.getElementById('query-arrow');
                        if (content && arrow) {
                            content.classList.toggle('expanded');
                            arrow.classList.toggle('expanded');
                        }
                    }

                    function showSuccess() {
                        const message = document.getElementById('successMessage');
                        if (message) {
                            message.classList.add('show');
                            setTimeout(() => {
                                message.classList.remove('show');
                            }, 2000);
                        }
                    }

                    function copyAsCsv() {
                        const columns = resultsData.columns;
                        const values = resultsData.values;

                        // Header row
                        let csv = columns.map(c => '"' + c.name.replace(/"/g, '""') + '"').join(',') + '\\n';

                        // Data rows
                        for (const row of values) {
                            csv += row.map(cell => {
                                if (cell === null || cell === undefined) return '';
                                if (typeof cell === 'string') return '"' + cell.replace(/"/g, '""') + '"';
                                return String(cell);
                            }).join(',') + '\\n';
                        }

                        navigator.clipboard.writeText(csv).then(showSuccess).catch(err => {
                            alert('Failed to copy: ' + err.message);
                        });
                    }

                    function copyAsJson() {
                        const columns = resultsData.columns;
                        const values = resultsData.values;

                        // Convert to array of objects
                        const rows = values.map(row => {
                            const obj = {};
                            columns.forEach((col, i) => {
                                obj[col.name] = row[i];
                            });
                            return obj;
                        });

                        navigator.clipboard.writeText(JSON.stringify(rows, null, 2)).then(showSuccess).catch(err => {
                            alert('Failed to copy: ' + err.message);
                        });
                    }
                </script>
            </body>
            </html>
        `;
    }

    private generateTableHtml(columns: EsqlColumn[], values: unknown[][]): string {
        if (columns.length === 0) {
            return '<div class="no-results">No results returned</div>';
        }

        let html = '<table class="results-table"><thead><tr>';

        // Header row with column names and types
        for (const col of columns) {
            html += `<th>${escapeHtml(col.name)}<span class="col-type">${escapeHtml(col.type)}</span></th>`;
        }
        html += '</tr></thead><tbody>';

        // Data rows or empty indicator
        if (values.length === 0) {
            html += `<tr><td colspan="${columns.length}" class="no-results">No rows returned</td></tr>`;
        } else {
            for (const row of values) {
                html += '<tr>';
                for (let i = 0; i < columns.length; i++) {
                    const value = row[i];
                    html += `<td>${this.formatCellValue(value, columns[i].type)}</td>`;
                }
                html += '</tr>';
            }
        }

        html += '</tbody></table>';
        return html;
    }

    private formatCellValue(value: unknown, type: string): string {
        if (value === null || value === undefined) {
            return '<span class="cell-null">null</span>';
        }

        if (typeof value === 'boolean') {
            return `<span class="cell-boolean ${value ? 'true' : 'false'}">${value}</span>`;
        }

        if (typeof value === 'number') {
            return `<span class="cell-number">${escapeHtml(String(value))}</span>`;
        }

        if (typeof value === 'object') {
            return `<span class="cell-object">${escapeHtml(JSON.stringify(value))}</span>`;
        }

        // For date types, try to format nicely
        if (type === 'date' || type === 'datetime') {
            try {
                const date = new Date(String(value));
                if (!isNaN(date.getTime())) {
                    return escapeHtml(date.toISOString());
                }
            } catch {
                // Date parsing failed, fall through to string rendering
            }
        }

        return escapeHtml(String(value));
    }
}
