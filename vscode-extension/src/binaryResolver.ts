/**
 * Binary resolution for LSP server and Python scripts.
 *
 * Provides intelligent resolution of executables:
 * - LSP Server: Bundled binary (production) or Python script (development)
 * - Grid Scripts: Always require Python
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import * as vscode from 'vscode';
import { ConfigService } from './configService';

export interface BinaryResolverResult {
    /** Path to the executable (binary or Python) */
    executable: string;
    /** Arguments to pass (empty for binary, [script_path] for Python) */
    args: string[];
    /** Working directory to use */
    cwd: string;
    /** Whether using bundled binary (true) or local development (false) */
    isBundled: boolean;
}

export class BinaryResolver {
    constructor(
        private readonly extensionPath: string,
        private readonly configService: ConfigService
    ) {}

    /**
     * Get platform-specific directory name (e.g., 'linux-x64', 'darwin-arm64').
     */
    private getPlatformDir(): string {
        const platform = process.platform;
        const arch = process.arch;

        let platformName: string;
        if (platform === 'win32') {
            platformName = 'win32';
        } else if (platform === 'darwin') {
            platformName = 'darwin';
        } else if (platform === 'linux') {
            platformName = 'linux';
        } else {
            throw new Error(`Unsupported platform: ${platform}`);
        }

        let archName: string;
        if (arch === 'x64') {
            archName = 'x64';
        } else if (arch === 'arm64') {
            archName = 'arm64';
        } else {
            throw new Error(`Unsupported architecture: ${arch}`);
        }

        return `${platformName}-${archName}`;
    }

    /**
     * Get the platform-specific binary name.
     */
    private getBinaryName(): string {
        return process.platform === 'win32' ? 'kb-dashboard-compiler-lsp.exe' : 'kb-dashboard-compiler-lsp';
    }

    /**
     * Get the expected path to the bundled binary.
     */
    private getBundledBinaryPath(): string {
        const platformDir = this.getPlatformDir();
        const binaryName = this.getBinaryName();
        return path.join(this.extensionPath, 'bin', platformDir, binaryName);
    }

    /**
     * Check if a file exists and is executable (Unix) or exists (Windows).
     */
    private isExecutable(filePath: string): boolean {
        if (!fs.existsSync(filePath)) {
            return false;
        }

        // On Windows, all files are "executable" if they exist
        if (process.platform === 'win32') {
            return true;
        }

        // On Unix, check executable bit
        try {
            fs.accessSync(filePath, fs.constants.X_OK);
            return true;
        } catch (error) {
            // File exists but isn't executable - expected for some files (e.g., non-bundled binaries)
            // Debug logging to aid troubleshooting in development
            console.debug(`File not executable: ${filePath}`, error);
            return false;
        }
    }

    /**
     * Resolve Python path for local development.
     *
     * Resolution order:
     * 1. Configured pythonPath setting (relative paths resolved to workspace)
     * 2. Workspace .venv/bin/python (or .venv/Scripts/python.exe on Windows)
     * 3. System 'python' command
     */
    private resolvePythonPath(outputChannel?: vscode.OutputChannel): string {
        const configuredPath = this.configService.getPythonPath();
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

        // Check explicitly configured Python path
        if (configuredPath !== 'python') {
            let resolvedPath: string;
            if (!path.isAbsolute(configuredPath)) {
                if (workspaceRoot) {
                    resolvedPath = path.join(workspaceRoot, configuredPath);
                } else {
                    outputChannel?.appendLine(`Warning: No workspace open, resolving relative path against extension: ${configuredPath}`);
                    resolvedPath = path.join(this.extensionPath, configuredPath);
                }
            } else {
                resolvedPath = configuredPath;
            }

            if (fs.existsSync(resolvedPath)) {
                outputChannel?.appendLine(`Using configured Python: ${resolvedPath}`);
                return resolvedPath;
            }

            outputChannel?.appendLine(`Warning: Configured Python not found: ${resolvedPath}`);
        }

        // Auto-detect workspace virtual environment
        if (workspaceRoot) {
            const venvPython = process.platform === 'win32'
                ? path.join(workspaceRoot, '.venv', 'Scripts', 'python.exe')
                : path.join(workspaceRoot, '.venv', 'bin', 'python');

            if (fs.existsSync(venvPython)) {
                outputChannel?.appendLine(`Using workspace venv: ${venvPython}`);
                return venvPython;
            }
        }

        // Fallback to system Python
        outputChannel?.appendLine('Using system Python: python');
        return 'python';
    }

    /**
     * Resolve LSP server configuration.
     *
     * Resolution order:
     * 1. Bundled binary in bin/{platform}-{arch}/kb-dashboard-compiler-lsp
     * 2. Python script (development fallback)
     */
    resolveLSPServer(outputChannel?: vscode.OutputChannel): BinaryResolverResult {
        // Check for bundled binary
        const binaryPath = this.getBundledBinaryPath();

        if (this.isExecutable(binaryPath)) {
            outputChannel?.appendLine(`Using bundled LSP binary: ${binaryPath}`);
            return {
                executable: binaryPath,
                args: [],
                cwd: this.extensionPath,
                isBundled: true
            };
        }

        // Fallback to Python module
        outputChannel?.appendLine(`Bundled binary not found at ${binaryPath}`);
        outputChannel?.appendLine('Falling back to Python LSP server module');

        const pythonPath = this.resolvePythonPath(outputChannel);

        // For development, use workspace root so dashboard_compiler can be imported
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        const cwd = workspaceRoot ?? path.dirname(this.extensionPath);

        outputChannel?.appendLine(`Using local Python LSP server: ${pythonPath} -m dashboard_compiler.lsp.server`);
        outputChannel?.appendLine(`Working directory: ${cwd}`);

        return {
            executable: pythonPath,
            args: ['-m', 'dashboard_compiler.lsp.server'],
            cwd,
            isBundled: false
        };
    }

    /**
     * Resolve Python executable for standalone scripts (grid extractor/updater).
     *
     * These scripts are NOT bundled as binaries - they always use Python.
     */
    resolvePythonForScripts(outputChannel?: vscode.OutputChannel): string {
        return this.resolvePythonPath(outputChannel);
    }
}
