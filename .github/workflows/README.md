# GitHub Actions Reusable Workflows

This directory contains reusable workflows and composite actions to reduce duplication across Claude-based workflows.

## Components

### 1. Composite Action: `setup-python-env`

**Location:** `.github/actions/setup-python-env/action.yml`

**Purpose:** Sets up Python environment with UV package manager. Can be used by any workflow that needs Python.

**Inputs:**
- `python-version` (optional, default: '3.12'): Python version to install
- `checkout-ref` (optional, default: ''): Git ref to checkout
- `fetch-depth` (optional, default: '1'): Number of commits to fetch
- `install-dependencies` (optional, default: 'false'): Whether to run `uv sync --all-extras`

**Usage in workflows:**
```yaml
steps:
  - name: Setup Python Environment
    uses: ./.github/actions/setup-python-env
    with:
      python-version: '3.12'
      install-dependencies: 'true'
```

**Use cases:**
- Test workflows (test.yml)
- Build workflows
- Any workflow requiring Python environment

### 2. Reusable Workflow: `run-claude`

**Location:** `.github/workflows/run-claude.yml`

**Purpose:** Executes Claude Code action with MCP servers configured. Centralizes all Claude-related setup.

**Inputs:**
- `python-version` (optional, default: '3.12'): Python version
- `checkout-ref` (optional, default: ''): Git ref to checkout
- `fetch-depth` (optional, default: 1): Fetch depth
- `prompt` (required): Prompt to pass to Claude
- `claude-args` (required): Arguments for Claude (allowed-tools, mcp-config path)
- `additional-permissions` (optional): Additional permissions in YAML format
- `track-progress` (optional, default: true): Whether to track progress
- `mcp-config` (optional): MCP server configuration JSON (has sensible defaults)

**Secrets:**
- `claude-oauth-token` (required): Claude OAuth token

**Usage in calling workflows:**
```yaml
jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      prompt: ${{ steps.set-prompt.outputs.PROMPT }}
    steps:
      - name: Set prompt
        id: set-prompt
        run: |
          cat >> $GITHUB_OUTPUT << 'EOF'
          PROMPT<<PROMPT_END
          Your prompt here...
          PROMPT_END
          EOF

  claude:
    needs: prepare
    permissions:
      contents: write
      pull-requests: write
      id-token: write
      actions: read
    uses: ./.github/workflows/run-claude.yml
    with:
      python-version: '3.10'
      prompt: ${{ needs.prepare.outputs.prompt }}
      claude-args: |
        --allowed-tools mcp__repository-summary,WebSearch
        --mcp-config /tmp/mcp-config/mcp-servers.json
    secrets:
      claude-oauth-token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

## Refactored Workflows

The following Claude workflows now use the reusable workflow:

1. **claude-on-mention.yml** - Responds to @claude mentions in issues/PRs
2. **claude-on-open-label.yml** - Triages new issues and labeled issues
3. **claude-on-issue-mention.yml** - Creates issues via @claude-issue mentions
4. **claude-on-merge-conflict.yml** - Resolves merge conflicts automatically
5. **claude-project-manager.yml** - Daily project management reviews

## Benefits

- **Reduced duplication**: 164 fewer lines of duplicate code across workflows
- **Easier maintenance**: Update environment setup or Claude configuration in one place
- **Consistency**: All Claude workflows use the same setup process
- **Flexibility**: Configurable parameters allow customization per workflow
- **Reusability**: The setup-python-env action can be used by non-Claude workflows

## Making Changes

### To update Python environment setup:
Edit `.github/actions/setup-python-env/action.yml`

### To update Claude execution logic:
Edit `.github/workflows/run-claude.yml`

### To update MCP server configuration for a specific workflow:
Pass custom `mcp-config` input when calling the reusable workflow.

### To add a new Claude workflow:
1. Create a `prepare` job to generate the prompt (with GitHub context)
2. Create a `claude` job that calls `.github/workflows/run-claude.yml`
3. Pass the prompt from the prepare job to the claude job

## Architecture Notes

**Why separate prepare and claude jobs?**
- Prompts often need GitHub context variables (issue numbers, PR refs, etc.)
- These must be evaluated in the calling workflow, not the reusable workflow
- Reusable workflows have limited access to caller's GitHub context

**Why inline environment setup in run-claude.yml?**
- Composite actions can't be called from reusable workflows with relative paths
- Inlining avoids complexity while keeping the code DRY
- The composite action remains available for non-Claude workflows

**Why pass MCP config as input?**
- Some workflows need different MCP server configurations
- Allows flexibility while providing sensible defaults
- Alternative would be multiple reusable workflows (more complexity)
