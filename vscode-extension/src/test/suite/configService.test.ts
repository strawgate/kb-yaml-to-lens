import * as assert from 'assert';
import * as vscode from 'vscode';
import { ConfigService } from '../../configService';

suite('ConfigService Test Suite', () => {
    let configService: ConfigService;
    let mockContext: vscode.ExtensionContext;

    suiteSetup(async () => {
        // Get the extension and activate it
        const extension = vscode.extensions.getExtension('strawgate.yaml-dashboard-compiler');
        assert.ok(extension);

        if (!extension.isActive) {
            await extension.activate();
        }

        // Create mock context for testing
        mockContext = {
            secrets: {
                store: async (key: string, value: string) => {
                    await vscode.workspace.getConfiguration().update(`test.${key}`, value, vscode.ConfigurationTarget.Global);
                },
                get: async (key: string) => {
                    return vscode.workspace.getConfiguration().get<string>(`test.${key}`);
                },
                delete: async (key: string) => {
                    await vscode.workspace.getConfiguration().update(`test.${key}`, undefined, vscode.ConfigurationTarget.Global);
                }
            }
        } as unknown as vscode.ExtensionContext;

        configService = new ConfigService(mockContext);
    });

    test('Should get default Kibana URL', () => {
        const url = configService.getKibanaUrl();
        assert.strictEqual(url, 'http://localhost:5601');
    });

    test('Should get default SSL verify setting', () => {
        const sslVerify = configService.getKibanaSslVerify();
        assert.strictEqual(sslVerify, true);
    });

    test('Should get default browser type', () => {
        const browserType = configService.getKibanaBrowserType();
        assert.strictEqual(browserType, 'external');
    });

    test('Should store and retrieve username', async () => {
        const testUsername = 'testuser';
        await configService.setKibanaUsername(testUsername);
        const retrievedUsername = await configService.getKibanaUsername();
        assert.strictEqual(retrievedUsername, testUsername);
    });

    test('Should store and retrieve password', async () => {
        const testPassword = 'testpass123';
        await configService.setKibanaPassword(testPassword);
        const retrievedPassword = await configService.getKibanaPassword();
        assert.strictEqual(retrievedPassword, testPassword);
    });

    test('Should store and retrieve API key', async () => {
        const testApiKey = 'test-api-key-12345';
        await configService.setKibanaApiKey(testApiKey);
        const retrievedApiKey = await configService.getKibanaApiKey();
        assert.strictEqual(retrievedApiKey, testApiKey);
    });

    test('Should clear username when set to empty string', async () => {
        await configService.setKibanaUsername('testuser');
        await configService.setKibanaUsername('');
        const username = await configService.getKibanaUsername();
        assert.strictEqual(username, '');
    });

    test('Should clear password when set to empty string', async () => {
        await configService.setKibanaPassword('testpass');
        await configService.setKibanaPassword('');
        const password = await configService.getKibanaPassword();
        assert.strictEqual(password, '');
    });

    test('Should clear API key when set to empty string', async () => {
        await configService.setKibanaApiKey('testkey');
        await configService.setKibanaApiKey('');
        const apiKey = await configService.getKibanaApiKey();
        assert.strictEqual(apiKey, '');
    });

    test('Should clear all credentials', async () => {
        // Set all credentials
        await configService.setKibanaUsername('user');
        await configService.setKibanaPassword('pass');
        await configService.setKibanaApiKey('key');

        // Clear all
        await configService.clearKibanaCredentials();

        // Verify all cleared
        const username = await configService.getKibanaUsername();
        const password = await configService.getKibanaPassword();
        const apiKey = await configService.getKibanaApiKey();

        assert.strictEqual(username, '');
        assert.strictEqual(password, '');
        assert.strictEqual(apiKey, '');
    });

    test('Should return empty string for non-existent credentials', async () => {
        // Clear first
        await configService.clearKibanaCredentials();

        const username = await configService.getKibanaUsername();
        const password = await configService.getKibanaPassword();
        const apiKey = await configService.getKibanaApiKey();

        assert.strictEqual(username, '');
        assert.strictEqual(password, '');
        assert.strictEqual(apiKey, '');
    });
});
