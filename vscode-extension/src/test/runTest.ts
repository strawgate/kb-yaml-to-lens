import * as path from 'path';
import { runTests, download, resolveCliArgsFromVSCodeExecutablePath } from '@vscode/test-electron';
import * as child_process from 'child_process';

async function main() {
    try {
        // Download VS Code first
        const vscodeExecutablePath = await download();

        // Install the required dependency extension
        const [cliPath, ...cliCommonArguments] =
            resolveCliArgsFromVSCodeExecutablePath(vscodeExecutablePath);

        const installResult = child_process.spawnSync(
            cliPath,
            [...cliCommonArguments, '--install-extension', 'redhat.vscode-yaml', '--force'],
            { encoding: 'utf-8', stdio: 'inherit' }
        );

        if (installResult.status !== 0) {
            throw new Error('Failed to install redhat.vscode-yaml extension');
        }

        // The folder containing the Extension Manifest package.json
        const extensionDevelopmentPath = path.resolve(__dirname, '../../');

        // The path to the extension test script
        const extensionTestsPath = path.resolve(__dirname, './suite/index');

        // Download VS Code, unzip it and run the integration test
        await runTests({
            vscodeExecutablePath,
            extensionDevelopmentPath,
            extensionTestsPath
            // Note: --disable-extensions is not used because it would disable redhat.vscode-yaml
            // which is a required dependency. The extension is installed above and will be
            // available during testing.
        });
    } catch (err) {
        console.error('Failed to run tests:', err);
        process.exit(1);
    }
}

main();
