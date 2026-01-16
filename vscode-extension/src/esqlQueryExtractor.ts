/**
 * Utilities for extracting ES|QL queries from YAML dashboard files.
 *
 * Detects ES|QL query blocks based on cursor position and extracts
 * the query text for execution.
 */

import * as vscode from 'vscode';

export interface ExtractedEsqlQuery {
    query: string;
    range: vscode.Range;
}

/**
 * Extracts an ES|QL query from the YAML document at the cursor position.
 *
 * Looks for `esql.query` or `query:` patterns in the document and extracts
 * the query text if the cursor is within or near the query block.
 *
 * @param document The VS Code text document
 * @param position The cursor position
 * @returns The extracted query if found, undefined otherwise
 */
export function extractEsqlQueryAtPosition(
    document: vscode.TextDocument,
    position: vscode.Position
): ExtractedEsqlQuery | undefined {
    const text = document.getText();
    const lines = text.split('\n');
    const cursorLine = position.line;

    // First, try to find if we're inside a query: block
    // Look backwards for 'query:' or 'query: |' pattern
    let queryStartLine = -1;
    let queryIndent = -1;
    let isMultiline = false;

    for (let i = cursorLine; i >= 0; i--) {
        const line = lines[i];
        const trimmed = line.trim();

        // Check for 'query:' pattern (with optional | for multiline)
        const queryMatch = line.match(/^(\s*)query:\s*(\|)?(.*)$/);
        if (queryMatch) {
            queryStartLine = i;
            queryIndent = queryMatch[1].length;
            isMultiline = queryMatch[2] === '|';

            // If it's an inline query (not multiline), extract from same line
            // Only match if cursor is on this line to avoid executing unintended queries
            if (!isMultiline && queryMatch[3] && queryMatch[3].trim().length > 0) {
                if (cursorLine !== i) {
                    // Cursor is not on the inline query line, don't return it
                    queryStartLine = -1;
                    queryIndent = -1;
                    break;
                }
                const inlineQuery = queryMatch[3].trim();
                // Remove quotes if present
                const cleanQuery = inlineQuery.replace(/^["']|["']$/g, '');
                return {
                    query: cleanQuery,
                    range: new vscode.Range(i, 0, i, line.length)
                };
            }
            break;
        }

        // If we hit a line with less or equal indent that's not whitespace/continuation,
        // and it's not a query line, we've gone too far
        const currentIndent = line.match(/^(\s*)/)?.[1].length ?? 0;
        if (trimmed.length > 0 && !trimmed.startsWith('-') && !trimmed.startsWith('#')) {
            // Check if this is a YAML key at a higher level
            if (currentIndent <= queryIndent && i < cursorLine && queryIndent !== -1) {
                break;
            }
        }
    }

    if (queryStartLine === -1) {
        // Also check if cursor is on a line with 'query:' prefix
        const currentLine = lines[cursorLine];
        const directMatch = currentLine.match(/^(\s*)query:\s*(\|)?(.*)$/);
        if (directMatch) {
            queryStartLine = cursorLine;
            queryIndent = directMatch[1].length;
            isMultiline = directMatch[2] === '|';

            if (!isMultiline && directMatch[3] && directMatch[3].trim().length > 0) {
                const inlineQuery = directMatch[3].trim().replace(/^["']|["']$/g, '');
                return {
                    query: inlineQuery,
                    range: new vscode.Range(cursorLine, 0, cursorLine, currentLine.length)
                };
            }
        }
    }

    if (queryStartLine === -1) {
        return undefined;
    }

    // For multiline queries, extract content from following lines
    if (isMultiline) {
        const queryLines: string[] = [];
        let queryEndLine = queryStartLine;
        const baseIndent = queryIndent + 2; // Multiline content is typically indented 2+ more

        for (let i = queryStartLine + 1; i < lines.length; i++) {
            const line = lines[i];

            // Empty lines are part of the query
            if (line.trim().length === 0) {
                queryLines.push('');
                queryEndLine = i;
                continue;
            }

            const lineIndent = line.match(/^(\s*)/)?.[1].length ?? 0;

            // If line is indented more than base, it's part of the query
            if (lineIndent >= baseIndent) {
                queryLines.push(line.slice(baseIndent));
                queryEndLine = i;
            } else {
                // We've exited the multiline block
                break;
            }
        }

        if (queryLines.length > 0) {
            // Check if cursor is within the query block
            if (cursorLine >= queryStartLine && cursorLine <= queryEndLine) {
                return {
                    query: queryLines.join('\n').trim(),
                    range: new vscode.Range(queryStartLine, 0, queryEndLine, lines[queryEndLine].length)
                };
            }
        }
    }

    // Handle array format queries: query: \n  - FROM logs-* \n  - WHERE ...
    const arrayQueryLines: string[] = [];
    let arrayEndLine = queryStartLine;
    const arrayBaseIndent = queryIndent + 2;

    for (let i = queryStartLine + 1; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();

        // Empty lines might be separators
        if (trimmed.length === 0) {
            continue;
        }

        const lineIndent = line.match(/^(\s*)/)?.[1].length ?? 0;

        // Check for array item (- prefix)
        if (lineIndent >= arrayBaseIndent && trimmed.startsWith('-')) {
            const content = trimmed.slice(1).trim().replace(/^["']|["']$/g, '');
            arrayQueryLines.push(content);
            arrayEndLine = i;
        } else if (lineIndent < arrayBaseIndent && trimmed.length > 0) {
            // We've exited the array block
            break;
        }
    }

    if (arrayQueryLines.length > 0) {
        // Check if cursor is within the query block
        if (cursorLine >= queryStartLine && cursorLine <= arrayEndLine) {
            // Join array items with pipe for ES|QL
            return {
                query: arrayQueryLines.join('\n| '),
                range: new vscode.Range(queryStartLine, 0, arrayEndLine, lines[arrayEndLine].length)
            };
        }
    }

    return undefined;
}

/**
 * Prompts the user to enter an ES|QL query manually.
 *
 * @returns The entered query or undefined if cancelled
 */
export async function promptForEsqlQuery(): Promise<string | undefined> {
    const query = await vscode.window.showInputBox({
        prompt: 'Enter ES|QL query to execute',
        placeHolder: 'FROM logs-* | STATS count = COUNT(*)',
        ignoreFocusOut: true,
        validateInput: (value) => {
            if (!value || value.trim().length === 0) {
                return 'Query is required';
            }
            // Basic validation: should contain FROM
            if (!value.toUpperCase().includes('FROM')) {
                return 'ES|QL query must contain FROM';
            }
            return undefined;
        }
    });

    return query?.trim();
}
