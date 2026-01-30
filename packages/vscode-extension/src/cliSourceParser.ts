/**
 * CLI source parsing utilities.
 *
 * This module contains pure functions for parsing CLI source configuration.
 * It has no VS Code dependencies, making it easy to unit test.
 */

/** GitHub repository URL for git-based installs */
export const GITHUB_REPO = 'https://github.com/strawgate/kb-yaml-to-lens';

/** Subdirectory in the repo containing the CLI package */
export const CLI_SUBDIRECTORY = 'packages/kb-dashboard-cli';

/** Type of CLI source */
export type CliSourceType = 'pypi' | 'git' | 'local';

/** Parsed CLI source configuration */
export interface CliSourceConfig {
    type: CliSourceType;
    /** Version for PyPI, branch/tag for git, or path for local */
    value: string;
}

/**
 * Parse a CLI source string to determine how to run the CLI.
 *
 * @param source The source string from settings
 * @param defaultVersion The default version to use if source is empty
 * @param isWindows Whether running on Windows (for path detection)
 * @returns Parsed CLI source configuration
 */
export function parseCliSource(source: string, defaultVersion: string, isWindows: boolean = false): CliSourceConfig {
    const trimmed = source.trim();

    // Check if it's "main" or another branch name (simple identifier)
    if (trimmed === 'main' || trimmed === 'master') {
        return { type: 'git', value: trimmed };
    }

    // Check if it looks like a local path (starts with / or contains path separators)
    if (trimmed.startsWith('/') || trimmed.startsWith('~') ||
        trimmed.startsWith('./') || trimmed.startsWith('../') ||
        (isWindows && /^[a-zA-Z]:/.test(trimmed))) {
        return { type: 'local', value: trimmed };
    }

    // Check if it looks like a version number (digits and dots)
    if (/^\d+\.\d+/.test(trimmed)) {
        return { type: 'pypi', value: trimmed };
    }

    // Check if it looks like a git ref (branch, tag, or commit hash)
    if (/^[a-zA-Z0-9._-]+$/.test(trimmed)) {
        return { type: 'git', value: trimmed };
    }

    // Default to treating it as a version (use default version if empty)
    return { type: 'pypi', value: trimmed || defaultVersion };
}

/**
 * Build uvx/uv arguments for the given CLI source configuration.
 *
 * @param source CLI source configuration
 * @param command The command to run (e.g., 'lsp', 'python')
 * @returns Array of arguments for uv
 */
export function buildUvArgs(source: CliSourceConfig, command: string): string[] {
    switch (source.type) {
        case 'pypi':
            // uvx kb-dashboard-cli==VERSION command
            return ['tool', 'run', `kb-dashboard-cli==${source.value}`, command];

        case 'git': {
            // uvx --from "git+https://...@ref#subdirectory=..." kb-dashboard command
            const gitUrl = `git+${GITHUB_REPO}@${source.value}#subdirectory=${CLI_SUBDIRECTORY}`;
            return ['tool', 'run', '--from', gitUrl, 'kb-dashboard', command];
        }

        case 'local':
            // uv run --directory /path kb-dashboard command
            return ['run', '--directory', source.value, 'kb-dashboard', command];
    }
}
