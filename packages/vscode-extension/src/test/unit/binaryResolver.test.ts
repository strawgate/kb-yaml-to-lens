import { expect } from 'chai';
import { parseCliSource, buildUvArgs, GITHUB_REPO, CLI_SUBDIRECTORY } from '../../cliSourceParser';

suite('CLI Source Parser Test Suite', () => {
    const defaultVersion = '1.0.0';

    suite('parseCliSource', () => {
        suite('PyPI versions', () => {
            test('parses semver version', () => {
                const result = parseCliSource('0.2.5', defaultVersion);
                expect(result.type).to.equal('pypi');
                expect(result.value).to.equal('0.2.5');
            });

            test('parses version with patch', () => {
                const result = parseCliSource('1.2.3', defaultVersion);
                expect(result.type).to.equal('pypi');
                expect(result.value).to.equal('1.2.3');
            });

            test('parses version with pre-release', () => {
                const result = parseCliSource('1.0.0-alpha', defaultVersion);
                expect(result.type).to.equal('pypi');
                expect(result.value).to.equal('1.0.0-alpha');
            });

            test('parses two-part version', () => {
                const result = parseCliSource('2.0', defaultVersion);
                expect(result.type).to.equal('pypi');
                expect(result.value).to.equal('2.0');
            });
        });

        suite('Git branches', () => {
            test('recognizes main branch', () => {
                const result = parseCliSource('main', defaultVersion);
                expect(result.type).to.equal('git');
                expect(result.value).to.equal('main');
            });

            test('recognizes master branch', () => {
                const result = parseCliSource('master', defaultVersion);
                expect(result.type).to.equal('git');
                expect(result.value).to.equal('master');
            });

            test('recognizes feature branch', () => {
                const result = parseCliSource('feature-xyz', defaultVersion);
                expect(result.type).to.equal('git');
                expect(result.value).to.equal('feature-xyz');
            });

            test('recognizes branch with dots', () => {
                const result = parseCliSource('release-1.0', defaultVersion);
                expect(result.type).to.equal('git');
                expect(result.value).to.equal('release-1.0');
            });

            test('recognizes branch with underscores', () => {
                const result = parseCliSource('fix_bug_123', defaultVersion);
                expect(result.type).to.equal('git');
                expect(result.value).to.equal('fix_bug_123');
            });
        });

        suite('Local paths (Unix)', () => {
            test('recognizes absolute path', () => {
                const result = parseCliSource('/Users/dev/project', defaultVersion, false);
                expect(result.type).to.equal('local');
                expect(result.value).to.equal('/Users/dev/project');
            });

            test('recognizes home directory path', () => {
                const result = parseCliSource('~/projects/cli', defaultVersion, false);
                expect(result.type).to.equal('local');
                expect(result.value).to.equal('~/projects/cli');
            });

            test('recognizes relative path with ./', () => {
                const result = parseCliSource('./packages/cli', defaultVersion, false);
                expect(result.type).to.equal('local');
                expect(result.value).to.equal('./packages/cli');
            });

            test('recognizes relative path with ../', () => {
                const result = parseCliSource('../other-repo/cli', defaultVersion, false);
                expect(result.type).to.equal('local');
                expect(result.value).to.equal('../other-repo/cli');
            });
        });

        suite('Local paths (Windows)', () => {
            test('recognizes Windows drive path', () => {
                const result = parseCliSource('C:\\Users\\dev\\project', defaultVersion, true);
                expect(result.type).to.equal('local');
                expect(result.value).to.equal('C:\\Users\\dev\\project');
            });

            test('recognizes Windows drive with forward slashes', () => {
                const result = parseCliSource('D:/projects/cli', defaultVersion, true);
                expect(result.type).to.equal('local');
                expect(result.value).to.equal('D:/projects/cli');
            });

            test('does not recognize Windows path on Unix', () => {
                const result = parseCliSource('C:\\Users\\dev', defaultVersion, false);
                // On Unix, this would be interpreted as a git branch (contains backslashes, not valid)
                // Actually backslash is not in [a-zA-Z0-9._-], so it falls through to default
                expect(result.type).to.equal('pypi');
            });
        });

        suite('Default behavior', () => {
            test('uses default version for empty string', () => {
                const result = parseCliSource('', defaultVersion);
                expect(result.type).to.equal('pypi');
                expect(result.value).to.equal(defaultVersion);
            });

            test('trims whitespace', () => {
                const result = parseCliSource('  0.2.5  ', defaultVersion);
                expect(result.type).to.equal('pypi');
                expect(result.value).to.equal('0.2.5');
            });

            test('trims whitespace from main', () => {
                const result = parseCliSource('  main  ', defaultVersion);
                expect(result.type).to.equal('git');
                expect(result.value).to.equal('main');
            });

            test('uses default version for whitespace-only string', () => {
                const result = parseCliSource('   ', defaultVersion);
                expect(result.type).to.equal('pypi');
                expect(result.value).to.equal(defaultVersion);
            });
        });

        suite('Edge cases', () => {
            test('handles version starting with v (treated as git ref)', () => {
                const result = parseCliSource('v1.0.0', defaultVersion);
                // 'v1.0.0' matches git ref pattern [a-zA-Z0-9._-]+
                expect(result.type).to.equal('git');
                expect(result.value).to.equal('v1.0.0');
            });

            test('handles commit hash', () => {
                const result = parseCliSource('abc123def', defaultVersion);
                expect(result.type).to.equal('git');
                expect(result.value).to.equal('abc123def');
            });

            test('handles long commit hash', () => {
                const result = parseCliSource('abc123def456789', defaultVersion);
                expect(result.type).to.equal('git');
                expect(result.value).to.equal('abc123def456789');
            });
        });
    });

    suite('buildUvArgs', () => {
        suite('PyPI source', () => {
            test('builds correct args for lsp command', () => {
                const args = buildUvArgs({ type: 'pypi', value: '0.2.5' }, 'lsp');
                expect(args).to.deep.equal(['tool', 'run', 'kb-dashboard-cli==0.2.5', 'lsp']);
            });

            test('builds correct args for python command', () => {
                const args = buildUvArgs({ type: 'pypi', value: '1.0.0' }, 'python');
                expect(args).to.deep.equal(['tool', 'run', 'kb-dashboard-cli==1.0.0', 'python']);
            });
        });

        suite('Git source', () => {
            test('builds correct args for main branch', () => {
                const args = buildUvArgs({ type: 'git', value: 'main' }, 'lsp');
                const expectedGitUrl = `git+${GITHUB_REPO}@main#subdirectory=${CLI_SUBDIRECTORY}`;
                expect(args).to.deep.equal(['tool', 'run', '--from', expectedGitUrl, 'kb-dashboard', 'lsp']);
            });

            test('builds correct args for feature branch', () => {
                const args = buildUvArgs({ type: 'git', value: 'feature-xyz' }, 'lsp');
                const expectedGitUrl = `git+${GITHUB_REPO}@feature-xyz#subdirectory=${CLI_SUBDIRECTORY}`;
                expect(args).to.deep.equal(['tool', 'run', '--from', expectedGitUrl, 'kb-dashboard', 'lsp']);
            });
        });

        suite('Local source', () => {
            test('builds correct args for local path', () => {
                const args = buildUvArgs({ type: 'local', value: '/path/to/cli' }, 'lsp');
                expect(args).to.deep.equal(['run', '--directory', '/path/to/cli', 'kb-dashboard', 'lsp']);
            });

            test('builds correct args for relative path', () => {
                const args = buildUvArgs({ type: 'local', value: './packages/cli' }, 'python');
                expect(args).to.deep.equal(['run', '--directory', './packages/cli', 'kb-dashboard', 'python']);
            });
        });
    });
});
