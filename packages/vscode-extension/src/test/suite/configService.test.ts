import * as assert from 'assert';
import * as vscode from 'vscode';
import { ConfigService } from '../../configService';

suite('ConfigService Test Suite', () => {
    let configService: ConfigService;
    let mockContext: vscode.ExtensionContext;
    let secretsStore: Map<string, string>;

    suiteSetup(async () => {
        // Get the extension and activate it
        const extension = vscode.extensions.getExtension('strawgate.kb-dashboard-compiler');
        assert.ok(extension);

        if (!extension.isActive) {
            await extension.activate();
        }

        // Create in-memory secrets store for testing
        secretsStore = new Map<string, string>();

        // Create mock context for testing
        mockContext = {
            secrets: {
                store: async (key: string, value: string) => {
                    secretsStore.set(key, value);
                },
                get: async (key: string) => {
                    return secretsStore.get(key);
                },
                delete: async (key: string) => {
                    secretsStore.delete(key);
                }
            }
        } as unknown as vscode.ExtensionContext;

        configService = new ConfigService(mockContext);
    });

    setup(() => {
        // Reset secrets store before each test to ensure isolation
        secretsStore.clear();
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

    interface CredentialCase {
        label: string;
        value: string;
        secretKey: string;
        setter: (val: string) => Promise<void>;
        getter: () => Promise<string>;
    }

    const credentialCases: CredentialCase[] = [
        {
            label: 'username',
            value: 'testuser',
            secretKey: 'yamlDashboard.kibana.username',
            setter: (val: string) => configService.setKibanaUsername(val),
            getter: () => configService.getKibanaUsername(),
        },
        {
            label: 'password',
            value: 'testpass123',
            secretKey: 'yamlDashboard.kibana.password',
            setter: (val: string) => configService.setKibanaPassword(val),
            getter: () => configService.getKibanaPassword(),
        },
        {
            label: 'API key',
            value: 'test-api-key-12345',
            secretKey: 'yamlDashboard.kibana.apiKey',
            setter: (val: string) => configService.setKibanaApiKey(val),
            getter: () => configService.getKibanaApiKey(),
        },
    ];

    for (const credential of credentialCases) {
        test(`Should store and retrieve ${credential.label}`, async () => {
            await credential.setter(credential.value);
            const retrieved = await credential.getter();
            assert.strictEqual(retrieved, credential.value);
        });

        test(`Should delete ${credential.label} from storage when set to empty string`, async () => {
            await credential.setter(credential.value);
            assert.ok(secretsStore.has(credential.secretKey), 'Secret should exist before clearing');
            await credential.setter('');
            assert.ok(!secretsStore.has(credential.secretKey), 'Secret should be deleted from storage');
            const cleared = await credential.getter();
            assert.strictEqual(cleared, '');
        });
    }

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
