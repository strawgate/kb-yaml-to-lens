import * as vscode from 'vscode';

/**
 * Service for accessing extension configuration settings.
 * Provides type-safe access to yamlDashboard configuration with default values.
 */
export class ConfigService {
    // eslint-disable-next-line @typescript-eslint/naming-convention
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
     * Gets the Kibana URL setting.
     * @returns The configured Kibana URL
     */
    static getKibanaUrl(): string {
        return this.get<string>('kibana.url', 'http://localhost:5601');
    }

    /**
     * Gets the Kibana username setting.
     * @returns The configured Kibana username
     */
    static getKibanaUsername(): string {
        return this.get<string>('kibana.username', '');
    }

    /**
     * Gets the Kibana password setting.
     * @returns The configured Kibana password
     */
    static getKibanaPassword(): string {
        return this.get<string>('kibana.password', '');
    }

    /**
     * Gets the Kibana API key setting.
     * @returns The configured Kibana API key
     */
    static getKibanaApiKey(): string {
        return this.get<string>('kibana.apiKey', '');
    }

    /**
     * Gets the Kibana SSL verify setting.
     * @returns True if SSL verification is enabled, false otherwise
     */
    static getKibanaSslVerify(): boolean {
        return this.get<boolean>('kibana.sslVerify', true);
    }

    /**
     * Gets the Kibana browser type setting.
     * @returns The browser type ('external' or 'simple')
     */
    static getKibanaBrowserType(): 'external' | 'simple' {
        return this.get<'external' | 'simple'>('kibana.browserType', 'external');
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
