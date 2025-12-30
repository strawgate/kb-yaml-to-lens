import * as vscode from 'vscode';

/**
 * Service for accessing extension configuration settings.
 * Provides type-safe access to yamlDashboard configuration with default values.
 */
export class ConfigService {
    private static readonly CONFIG_SECTION = 'yamlDashboard';

    /**
     * Gets the Python path setting.
     * @returns The configured Python path, or 'python' as default
     */
    static getPythonPath(): string {
        return this.get<string>('pythonPath', 'python');
    }

    /**
     * Gets the compile on save setting.
     * @returns True if compile on save is enabled, false otherwise
     */
    static getCompileOnSave(): boolean {
        return this.get<boolean>('compileOnSave', true);
    }

    /**
     * Gets a configuration value with a default fallback.
     * @param key The configuration key
     * @param defaultValue The default value if not set
     * @returns The configuration value
     */
    private static get<T>(key: string, defaultValue: T): T {
        return vscode.workspace.getConfiguration(this.CONFIG_SECTION).get<T>(key, defaultValue);
    }
}
