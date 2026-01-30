import * as vscode from 'vscode';

/**
 * Service for accessing extension configuration settings.
 * Provides type-safe access to yamlDashboard configuration with default values.
 *
 * Credentials (username, password, API key) are stored securely using VS Code's
 * SecretStorage API, which encrypts them using the OS keychain (macOS Keychain,
 * Windows Credential Manager, or Linux Secret Service).
 */
export class ConfigService {
    // eslint-disable-next-line @typescript-eslint/naming-convention
    private static readonly CONFIG_SECTION = 'yamlDashboard';
    // eslint-disable-next-line @typescript-eslint/naming-convention
    private static readonly SECRET_KEYS = {
        username: 'yamlDashboard.kibana.username',
        password: 'yamlDashboard.kibana.password',
        apiKey: 'yamlDashboard.kibana.apiKey'
    };

    private readonly secrets: vscode.SecretStorage;

    constructor(context: vscode.ExtensionContext) {
        this.secrets = context.secrets;
    }

    /**
     * Gets the CLI source setting.
     * @returns The configured CLI source (version, 'main', or local path), empty string means use extension version
     */
    getCliSource(): string {
        return ConfigService.get<string>('cli.source', '');
    }

    /**
     * Gets the Python path setting.
     * @returns The configured Python path, or 'python' as default
     */
    getPythonPath(): string {
        return ConfigService.get<string>('pythonPath', 'python');
    }

    /**
     * Gets the compile on save setting.
     * @returns True if compile on save is enabled, false otherwise
     */
    getCompileOnSave(): boolean {
        return ConfigService.get<boolean>('compileOnSave', true);
    }

    /**
     * Gets the Kibana URL setting.
     * @returns The configured Kibana URL
     */
    getKibanaUrl(): string {
        return ConfigService.get<string>('kibana.url', 'http://localhost:5601');
    }

    /**
     * Gets a credential from secure storage.
     * @param key The secret key to retrieve
     * @returns The credential value, or empty string if not set
     */
    private async getCredential(key: string): Promise<string> {
        try {
            return await this.secrets.get(key) ?? '';
        } catch (error) {
            console.error('Failed to retrieve credential:', error);
            return '';
        }
    }

    /**
     * Sets a credential in secure storage.
     * @param key The secret key to store
     * @param value The credential value to store
     * @param description Human-readable description for error messages
     */
    private async setCredential(key: string, value: string, description: string): Promise<void> {
        try {
            if (value) {
                await this.secrets.store(key, value);
            } else {
                await this.secrets.delete(key);
            }
        } catch (error) {
            throw new Error(`Failed to store ${description}: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }

    /**
     * Gets the Kibana username from secure storage.
     * @returns The configured Kibana username, or empty string if not set
     */
    async getKibanaUsername(): Promise<string> {
        return this.getCredential(ConfigService.SECRET_KEYS.username);
    }

    /**
     * Sets the Kibana username in secure storage.
     * @param username The username to store
     */
    async setKibanaUsername(username: string): Promise<void> {
        return this.setCredential(ConfigService.SECRET_KEYS.username, username, 'Kibana username');
    }

    /**
     * Gets the Kibana password from secure storage.
     * @returns The configured Kibana password, or empty string if not set
     */
    async getKibanaPassword(): Promise<string> {
        return this.getCredential(ConfigService.SECRET_KEYS.password);
    }

    /**
     * Sets the Kibana password in secure storage.
     * @param password The password to store
     */
    async setKibanaPassword(password: string): Promise<void> {
        return this.setCredential(ConfigService.SECRET_KEYS.password, password, 'Kibana password');
    }

    /**
     * Gets the Kibana API key from secure storage.
     * @returns The configured Kibana API key, or empty string if not set
     */
    async getKibanaApiKey(): Promise<string> {
        return this.getCredential(ConfigService.SECRET_KEYS.apiKey);
    }

    /**
     * Sets the Kibana API key in secure storage.
     * @param apiKey The API key to store
     */
    async setKibanaApiKey(apiKey: string): Promise<void> {
        return this.setCredential(ConfigService.SECRET_KEYS.apiKey, apiKey, 'Kibana API key');
    }

    /**
     * Clears all stored Kibana credentials.
     */
    async clearKibanaCredentials(): Promise<void> {
        try {
            await this.secrets.delete(ConfigService.SECRET_KEYS.username);
            await this.secrets.delete(ConfigService.SECRET_KEYS.password);
            await this.secrets.delete(ConfigService.SECRET_KEYS.apiKey);
        } catch (error) {
            throw new Error(`Failed to clear Kibana credentials: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }

    /**
     * Gets the Kibana SSL verify setting.
     * @returns True if SSL verification is enabled, false otherwise
     */
    getKibanaSslVerify(): boolean {
        return ConfigService.get<boolean>('kibana.sslVerify', true);
    }

    /**
     * Gets the Kibana browser type setting.
     * @returns The browser type ('external' or 'simple')
     */
    getKibanaBrowserType(): 'external' | 'simple' {
        return ConfigService.get<'external' | 'simple'>('kibana.browserType', 'external');
    }

    /**
     * Gets the Kibana open on save setting.
     * @returns True if open on save is enabled, false otherwise
     */
    getKibanaOpenOnSave(): boolean {
        return ConfigService.get<boolean>('kibana.openOnSave', false);
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
