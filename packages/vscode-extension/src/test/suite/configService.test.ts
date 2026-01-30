/* eslint-disable @typescript-eslint/no-unused-expressions */
import { expect } from 'chai';
import sinon from 'sinon';
import * as vscode from 'vscode';
import { ConfigService } from '../../configService';

suite('ConfigService Test Suite', () => {
    let configService: ConfigService;
    let mockContext: vscode.ExtensionContext;
    let secretsStore: Map<string, string>;
    let storeStub: sinon.SinonStub;
    let getStub: sinon.SinonStub;
    let deleteStub: sinon.SinonStub;

    suiteSetup(async () => {
        // Get the extension and activate it
        const extension = vscode.extensions.getExtension('strawgate.kb-dashboard-compiler');
        expect(extension).to.exist;

        if (extension && !extension.isActive) {
            await extension.activate();
        }

        // Create in-memory secrets store for testing
        secretsStore = new Map<string, string>();

        // Create sinon stubs for secrets API
        storeStub = sinon.stub().callsFake(async (key: string, value: string) => {
            secretsStore.set(key, value);
        });
        getStub = sinon.stub().callsFake(async (key: string) => {
            return secretsStore.get(key);
        });
        deleteStub = sinon.stub().callsFake(async (key: string) => {
            secretsStore.delete(key);
        });

        // Create mock context for testing with sinon stubs
        mockContext = {
            secrets: {
                store: storeStub,
                get: getStub,
                delete: deleteStub
            }
        } as unknown as vscode.ExtensionContext;

        configService = new ConfigService(mockContext);
    });

    setup(() => {
        // Reset secrets store and stub call history before each test
        secretsStore.clear();
        storeStub.resetHistory();
        getStub.resetHistory();
        deleteStub.resetHistory();
    });

    test('Should get default Kibana URL', () => {
        const url = configService.getKibanaUrl();
        expect(url).to.equal('http://localhost:5601');
    });

    test('Should get default SSL verify setting', () => {
        const sslVerify = configService.getKibanaSslVerify();
        expect(sslVerify).to.be.true;
    });

    test('Should get default browser type', () => {
        const browserType = configService.getKibanaBrowserType();
        expect(browserType).to.equal('external');
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
            expect(retrieved).to.equal(credential.value);
            expect(storeStub.calledWith(credential.secretKey, credential.value)).to.be.true;
        });

        test(`Should delete ${credential.label} from storage when set to empty string`, async () => {
            await credential.setter(credential.value);
            expect(secretsStore.has(credential.secretKey)).to.be.true;
            await credential.setter('');
            expect(secretsStore.has(credential.secretKey)).to.be.false;
            expect(deleteStub.calledWith(credential.secretKey)).to.be.true;
            const cleared = await credential.getter();
            expect(cleared).to.equal('');
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

        expect(username).to.equal('');
        expect(password).to.equal('');
        expect(apiKey).to.equal('');
    });

    test('Should return empty string for non-existent credentials', async () => {
        // Clear first
        await configService.clearKibanaCredentials();

        const username = await configService.getKibanaUsername();
        const password = await configService.getKibanaPassword();
        const apiKey = await configService.getKibanaApiKey();

        expect(username).to.equal('');
        expect(password).to.equal('');
        expect(apiKey).to.equal('');
    });
});
