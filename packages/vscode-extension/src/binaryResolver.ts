/**
 * Binary resolution for LSP server and Python scripts.
 *
 * Provides intelligent resolution of executables:
 * - LSP Server: Bundled uv with uvx to run published PyPI package (production)
 *               or Python script (development)
 * - Grid Scripts: Bundled uv or fallback to Python
 *
 * CLI source can be configured via yamlDashboard.cli.source setting:
 * - Version number (e.g., "0.2.5"): Fetches from PyPI
 * - "main": Fetches latest from GitHub main branch
 * - Local path: Uses local directory for development
 */

import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';
import { ConfigService } from './configService';
import { parseCliSource, buildUvArgs, type CliSourceConfig } from './cliSourceParser';

export interface BinaryResolverResult {
    /** Path to the executable (uv or Python) */
    executable: string;
    /** Arguments to pass */
    args: string[];
    /** Working directory to use */
    cwd: string;
    /** Whether using bundled uv (true) or local development (false) */
    isBundled: boolean;
}

export class BinaryResolver {
    constructor(
        private readonly extensionPath: string,
        private readonly configService: ConfigService,
        private readonly extensionVersion: string
    ) {}

    /**
     * Parse the CLI source setting to determine how to run the CLI.
     *
     * @returns Parsed CLI source configuration
     */
    private getCliSourceConfig(): CliSourceConfig {
        const source = this.configService.getCliSource();
        return parseCliSource(source, this.extensionVersion, process.platform === 'win32');
    }

    /**
     * Normalize CLI source by converting relative local paths to absolute paths.
     * This prevents double-resolution when both buildUvArgs and cwd use the same path.
     *
     * @param cliSource The CLI source configuration to normalize
     * @returns Normalized CLI source with absolute local path if applicable
     */
    private normalizeCliSource(cliSource: CliSourceConfig): CliSourceConfig {
        if (cliSource.type !== 'local') {
            return cliSource;
        }

        // If already absolute, return as-is
        if (path.isAbsolute(cliSource.value)) {
            return cliSource;
        }

        // Resolve relative path against workspace root, or extension path as fallback
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath ?? this.extensionPath;
        const resolvedPath = path.resolve(workspaceRoot, cliSource.value);

        return { ...cliSource, value: resolvedPath };
    }

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
     * Get the platform-specific uv binary name.
     */
    private getUvBinaryName(): string {
        return process.platform === 'win32' ? 'uv.exe' : 'uv';
    }

    /**
     * Get the expected path to the bundled uv binary.
     */
    private getBundledUvPath(): string {
        const platformDir = this.getPlatformDir();
        const binaryName = this.getUvBinaryName();
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
     * 1. Bundled uv with uvx to run CLI based on configured source
     * 2. Python script (development fallback when uv not available)
     */
    resolveLSPServer(outputChannel?: vscode.OutputChannel): BinaryResolverResult {
        const uvPath = this.getBundledUvPath();
        const cliSource = this.normalizeCliSource(this.getCliSourceConfig());

        // Check for bundled uv
        if (this.isExecutable(uvPath)) {
            outputChannel?.appendLine(`Using bundled uv: ${uvPath}`);

            // Log what source we're using
            switch (cliSource.type) {
                case 'pypi':
                    outputChannel?.appendLine(`Using kb-dashboard-cli==${cliSource.value} from PyPI`);
                    break;
                case 'git':
                    outputChannel?.appendLine(`Using kb-dashboard-cli from git (${cliSource.value} branch)`);
                    break;
                case 'local':
                    outputChannel?.appendLine(`Using local kb-dashboard-cli from ${cliSource.value}`);
                    break;
            }

            const args = buildUvArgs(cliSource, 'lsp');
            const cwd = cliSource.type === 'local' ? cliSource.value : process.cwd();

            return {
                executable: uvPath,
                args,
                cwd,
                isBundled: true
            };
        }

        // Fallback to Python module for development
        outputChannel?.appendLine(`Bundled uv not found at ${uvPath}`);
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
     * Resolve executable for standalone scripts (grid extractor/updater).
     *
     * Resolution order:
     * 1. Bundled uv with uvx (production mode)
     * 2. Python (development fallback)
     */
    resolveForScripts(outputChannel?: vscode.OutputChannel): BinaryResolverResult {
        const uvPath = this.getBundledUvPath();
        const cliSource = this.normalizeCliSource(this.getCliSourceConfig());

        // Check for bundled uv
        if (this.isExecutable(uvPath)) {
            outputChannel?.appendLine(`Using bundled uv for scripts: ${uvPath}`);

            const args = buildUvArgs(cliSource, 'python');
            const cwd = cliSource.type === 'local' ? cliSource.value : process.cwd();

            return {
                executable: uvPath,
                args,
                cwd,
                isBundled: true
            };
        }

        // Fallback to Python
        const pythonPath = this.resolvePythonPath(outputChannel);
        const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        const cwd = workspaceRoot ?? path.dirname(this.extensionPath);

        return {
            executable: pythonPath,
            args: [],
            cwd,
            isBundled: false
        };
    }
}
