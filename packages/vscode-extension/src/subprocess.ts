/**
 * Subprocess utilities using execa for reliable process execution.
 *
 * Replaces custom Promise wrappers around child_process.spawn with
 * the well-tested execa library for better error handling, timeout
 * support, and cross-platform compatibility.
 */

import { execa } from 'execa';
import * as path from 'path';
import { BinaryResolver } from './binaryResolver';
import { ConfigService } from './configService';

export interface RunPythonScriptOptions {
    /** Arguments to pass to the Python script (after -m module.name) */
    args: string[];
    /** Error context for error messages (e.g., "Grid extraction") */
    errorContext: string;
    /** Timeout in milliseconds (default: 30000) */
    timeout?: number;
}

export interface RunPythonScriptResult<T> {
    /** Parsed result from stdout */
    data: T;
    /** Raw stdout (for debugging) */
    stdout: string;
    /** Raw stderr (for debugging) */
    stderr: string;
}

/**
 * Run a Python script using the BinaryResolver to find the appropriate executor.
 *
 * @param extensionPath Path to the extension directory
 * @param configService Configuration service for resolving Python path
 * @param options Script execution options
 * @param parseResult Function to parse stdout into the desired type
 * @returns Parsed result from the script
 * @throws Error if the script fails or times out
 */
export async function runPythonScript<T>(
    extensionPath: string,
    configService: ConfigService,
    options: RunPythonScriptOptions,
    parseResult: (stdout: string) => T
): Promise<T> {
    const resolver = new BinaryResolver(extensionPath, configService);
    const resolved = resolver.resolveForScripts();

    const fullArgs = [...resolved.args, ...options.args];

    const result = await execa({
        cwd: resolved.isBundled ? resolved.cwd : path.join(extensionPath, '..'),
        timeout: options.timeout ?? 30000,
        reject: false, // Don't throw on non-zero exit, we'll handle it
    })`${resolved.executable} ${fullArgs}`;

    // Convert stdout/stderr to strings (execa v9 returns them as strings by default with default encoding)
    const stdout = typeof result.stdout === 'string' ? result.stdout : String(result.stdout ?? '');
    const stderr = typeof result.stderr === 'string' ? result.stderr : String(result.stderr ?? '');

    // Handle timeout
    if (result.timedOut) {
        const timeoutSec = (options.timeout ?? 30000) / 1000;
        throw new Error(
            `${options.errorContext} timed out after ${timeoutSec} seconds. stderr: ${stderr || '(empty)'}`
        );
    }

    // Handle spawn errors (e.g., executable not found)
    if (result.failed && result.exitCode === undefined) {
        throw new Error(`Failed to start Python: ${result.message || 'Unknown error'}`);
    }

    // Handle non-zero exit code
    if (result.exitCode !== 0) {
        throw new Error(`${options.errorContext} failed: ${stderr || stdout}`);
    }

    // Parse and return result
    try {
        return parseResult(stdout);
    } catch (error) {
        throw new Error(
            `Failed to parse result: ${error instanceof Error ? error.message : String(error)}`
        );
    }
}
