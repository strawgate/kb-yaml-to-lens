/**
 * Shared utilities for VS Code webview panels.
 * Provides common HTML escaping, loading content, and error content generation.
 */

/**
 * Escapes HTML special characters to prevent XSS attacks.
 * @param text - The text to escape
 * @returns HTML-escaped string
 */
export function escapeHtml(text: string): string {
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

/**
 * Generates a loading spinner HTML page for webview panels.
 * @param message - The loading message to display
 * @returns HTML string for loading state
 */
export function getLoadingContent(message: string = 'Loading...'): string {
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
                <h2>${escapeHtml(message)}</h2>
            </div>
        </body>
        </html>
    `;
}

/**
 * Generates an error page HTML for webview panels.
 * @param error - The error to display
 * @param title - The error title (defaults to 'Error')
 * @returns HTML string for error state
 */
export function getErrorContent(error: unknown, title: string = 'Error'): string {
    const errorMessage = error instanceof Error ? error.message : String(error);
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
            <h2>${escapeHtml(title)}</h2>
            <pre>${escapeHtml(errorMessage)}</pre>
        </body>
        </html>
    `;
}
