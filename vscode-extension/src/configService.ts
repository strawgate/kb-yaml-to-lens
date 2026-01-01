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
     * Gets the Kibana username from secure storage.
     * @returns The configured Kibana username, or empty string if not set
     */
    async getKibanaUsername(): Promise<string> {
        try {
            return await this.secrets.get(ConfigService.SECRET_KEYS.username) ?? '';
        } catch (error) {
            console.error('Failed to retrieve Kibana username:', error);
            return '';
        }
    }

    /**
     * Sets the Kibana username in secure storage.
     * @param username The username to store
     */
    async setKibanaUsername(username: string): Promise<void> {
        try {
            if (username) {
                await this.secrets.store(ConfigService.SECRET_KEYS.username, username);
            } else {
                await this.secrets.delete(ConfigService.SECRET_KEYS.username);
            }
        } catch (error) {
            throw new Error(`Failed to store Kibana username: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }

    /**
     * Gets the Kibana password from secure storage.
     * @returns The configured Kibana password, or empty string if not set
     */
    async getKibanaPassword(): Promise<string> {
        try {
            return await this.secrets.get(ConfigService.SECRET_KEYS.password) ?? '';
        } catch (error) {
            console.error('Failed to retrieve Kibana password:', error);
            return '';
        }
    }

    /**
     * Sets the Kibana password in secure storage.
     * @param password The password to store
     */
    async setKibanaPassword(password: string): Promise<void> {
        try {
            if (password) {
                await this.secrets.store(ConfigService.SECRET_KEYS.password, password);
            } else {
                await this.secrets.delete(ConfigService.SECRET_KEYS.password);
            }
        } catch (error) {
            throw new Error(`Failed to store Kibana password: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }

    /**
     * Gets the Kibana API key from secure storage.
     * @returns The configured Kibana API key, or empty string if not set
     */
    async getKibanaApiKey(): Promise<string> {
        try {
            return await this.secrets.get(ConfigService.SECRET_KEYS.apiKey) ?? '';
        } catch (error) {
            console.error('Failed to retrieve Kibana API key:', error);
            return '';
        }
    }

    /**
     * Sets the Kibana API key in secure storage.
     * @param apiKey The API key to store
     */
    async setKibanaApiKey(apiKey: string): Promise<void> {
        try {
            if (apiKey) {
                await this.secrets.store(ConfigService.SECRET_KEYS.apiKey, apiKey);
            } else {
                await this.secrets.delete(ConfigService.SECRET_KEYS.apiKey);
            }
        } catch (error) {
            throw new Error(`Failed to store Kibana API key: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
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
     * Gets the Kibana upload on save setting.
     * @returns True if upload on save is enabled, false otherwise
     */
    getKibanaUploadOnSave(): boolean {
        return ConfigService.get<boolean>('kibana.uploadOnSave', false);
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
