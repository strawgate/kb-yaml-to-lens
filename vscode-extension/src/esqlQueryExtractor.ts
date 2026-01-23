/**
 * Utilities for extracting ES|QL queries from YAML dashboard files.
 *
 * Uses the eemeli/yaml library for proper AST parsing with position tracking.
 */

import * as vscode from 'vscode';
import { parseDocument, LineCounter, isScalar, isSeq, isMap, YAMLSeq, Pair, Node } from 'yaml';

export interface ExtractedEsqlQuery {
    query: string;
    range: vscode.Range;
}

/**
 * Flattens a potentially nested YAML sequence into a list of scalar string values.
 *
 * This handles YAML anchors that create nested lists, e.g.:
 *   .base: &base_query
 *     - FROM logs-*
 *   query:
 *     - *base_query
 *     - WHERE x > 0
 *
 * becomes: ["FROM logs-*", "WHERE x > 0"]
 */
function flattenSequenceItems(seq: YAMLSeq): string[] {
    const result: string[] = [];
    for (const item of seq.items) {
        if (isScalar(item)) {
            result.push(String(item.value));
        } else if (isSeq(item)) {
            // Recursively flatten nested sequences
            result.push(...flattenSequenceItems(item as YAMLSeq));
        }
    }
    return result;
}

/**
 * Finds a query node in the YAML AST that contains the given offset.
 *
 * Recursively searches for `query` or `esql.query` keys in the document
 * and returns the value if the cursor is within the node's range.
 */
function findQueryAtOffset(
    node: unknown,
    offset: number
): { value: string; range: [number, number, number] } | undefined {
    if (!node) {
        return undefined;
    }

    // Handle Map nodes - look for 'query' or 'esql.query' keys
    if (isMap(node)) {
        for (const item of node.items) {
            const pair = item as Pair;
            const key = pair.key;
            const value = pair.value;

            // Check if this is a 'query' or 'esql.query' key
            if (isScalar(key)) {
                const keyName = String(key.value);
                if (keyName === 'query' || keyName === 'esql.query') {
                    // Check if cursor is within this key-value pair's range
                    const keyRange = key.range;
                    const valueNode = value as Node | null;

                    if (keyRange && valueNode?.range) {
                        const pairStart = keyRange[0];
                        const pairEnd = valueNode.range[2];

                        // If cursor is within this pair
                        if (offset >= pairStart && offset <= pairEnd) {
                            // Extract the query value
                            if (isScalar(valueNode)) {
                                const queryValue = String(valueNode.value);
                                return {
                                    value: queryValue,
                                    range: [pairStart, valueNode.range[1], pairEnd]
                                };
                            } else if (isSeq(valueNode)) {
                                // Handle array format: query: ["FROM logs", "WHERE x > 0"]
                                // Also handles nested sequences from YAML anchors
                                const queryParts = flattenSequenceItems(valueNode as YAMLSeq);
                                if (queryParts.length > 0) {
                                    return {
                                        value: queryParts.join('\n| '),
                                        range: [pairStart, valueNode.range[1], pairEnd]
                                    };
                                }
                            }
                        }
                    }
                }
            }

            // Recursively search in the value
            const result = findQueryAtOffset(value, offset);
            if (result) {
                return result;
            }
        }
    }

    // Handle Sequence nodes - search in items
    if (isSeq(node)) {
        for (const item of (node as YAMLSeq).items) {
            const result = findQueryAtOffset(item, offset);
            if (result) {
                return result;
            }
        }
    }

    return undefined;
}

/**
 * Converts a character offset to a VS Code Position.
 */
function offsetToPosition(lineCounter: LineCounter, offset: number): vscode.Position {
    const pos = lineCounter.linePos(offset);
    // linePos returns 1-indexed line and col, VS Code uses 0-indexed
    return new vscode.Position(pos.line - 1, pos.col - 1);
}

/**
 * Extracts an ES|QL query from the YAML document at the cursor position.
 *
 * Uses proper YAML AST parsing to find `query:` or `esql.query:` nodes
 * and extracts the query text if the cursor is within the node.
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

    // Set up line counter for position tracking
    const lineCounter = new LineCounter();
    const doc = parseDocument(text, { lineCounter });

    // Check for YAML parse errors
    if (doc.errors.length > 0) {
        console.error('YAML parse errors in ES|QL extraction:', doc.errors);
        return undefined;
    }

    // Convert cursor position to offset
    const cursorOffset = document.offsetAt(position);

    // Find query node at cursor position
    const result = findQueryAtOffset(doc.contents, cursorOffset);

    if (!result) {
        return undefined;
    }

    // Convert range offsets to VS Code positions
    const startPos = offsetToPosition(lineCounter, result.range[0]);
    const endPos = offsetToPosition(lineCounter, result.range[2]);

    return {
        query: result.value.trim(),
        range: new vscode.Range(startPos, endPos)
    };
}

/**
 * Extracts selected text from the active editor as an ES|QL query.
 *
 * @param document The VS Code text document
 * @param selection The current selection
 * @returns The selected text if valid, undefined otherwise
 */
export function extractSelectedText(
    document: vscode.TextDocument,
    selection: vscode.Selection
): ExtractedEsqlQuery | undefined {
    if (selection.isEmpty) {
        return undefined;
    }

    const selectedText = document.getText(selection).trim();
    if (!selectedText) {
        return undefined;
    }

    return {
        query: selectedText,
        range: new vscode.Range(selection.start, selection.end)
    };
}

/**
 * Prompts the user to enter an ES|QL query manually.
 *
 * @returns The entered query or undefined if cancelled
 */
export async function promptForEsqlQuery(): Promise<string | undefined> {
    try {
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
    } catch (err) {
        console.error('Failed to prompt for ES|QL query:', err);
        return undefined;
    }
}
