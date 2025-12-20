# Claude Project Manager Workflow

This document contains the complete specification for a GitHub Actions workflow that acts as an automated project manager, reviewing the repository daily and filing issues with actionable items for maintainers.

## Workflow File

Create this file at `.github/workflows/claude-project-manager.yml`:

```yaml
name: Claude Project Manager

on:
  schedule:
    # Run daily at 9 AM UTC (adjust as needed)
    - cron: '0 9 * * *'
  workflow_dispatch: # Allow manual triggering

permissions:
  contents: read
  issues: write
  pull-requests: read
  actions: read

jobs:
  check-activity:
    runs-on: ubuntu-latest
    outputs:
      has_activity: ${{ steps.check.outputs.has_activity }}
      last_pm_issue: ${{ steps.check.outputs.last_pm_issue }}
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 50 # Fetch enough history to check recent activity

      - name: Check for recent activity
        id: check
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Get the last open Project Manager issue number
          LAST_PM_ISSUE=$(gh issue list \
            --label "project-manager" \
            --state open \
            --limit 1 \
            --json number \
            --jq '.[0].number // ""')
          
          echo "last_pm_issue=$LAST_PM_ISSUE" >> $GITHUB_OUTPUT
          
          # If there's an open PM issue, check if there's been activity since it was created
          if [ -n "$LAST_PM_ISSUE" ]; then
            echo "Found open PM issue #$LAST_PM_ISSUE"
            
            # Get the creation date of the last PM issue
            ISSUE_CREATED=$(gh issue view "$LAST_PM_ISSUE" --json createdAt --jq '.createdAt')
            
            # Check for commits since the issue was created
            COMMIT_COUNT=$(git log --since="$ISSUE_CREATED" --oneline | wc -l)
            
            # Check for new issues (excluding PM issues)
            NEW_ISSUES=$(gh issue list \
              --search "created:>=$ISSUE_CREATED -label:project-manager" \
              --limit 100 \
              --json number \
              --jq 'length')
            
            # Check for new PRs
            NEW_PRS=$(gh pr list \
              --search "created:>=$ISSUE_CREATED" \
              --limit 100 \
              --json number \
              --jq 'length')
            
            # Check for PR merges
            MERGED_PRS=$(gh pr list \
              --search "merged:>=$ISSUE_CREATED" \
              --state merged \
              --limit 100 \
              --json number \
              --jq 'length')
            
            TOTAL_ACTIVITY=$((COMMIT_COUNT + NEW_ISSUES + NEW_PRS + MERGED_PRS))
            
            echo "Activity since last PM issue:"
            echo "  Commits: $COMMIT_COUNT"
            echo "  New Issues: $NEW_ISSUES"
            echo "  New PRs: $NEW_PRS"
            echo "  Merged PRs: $MERGED_PRS"
            echo "  Total: $TOTAL_ACTIVITY"
            
            if [ $TOTAL_ACTIVITY -lt 3 ]; then
              echo "Not enough activity to create new PM issue"
              echo "has_activity=false" >> $GITHUB_OUTPUT
            else
              echo "Sufficient activity detected"
              echo "has_activity=true" >> $GITHUB_OUTPUT
            fi
          else
            echo "No open PM issue found, will create one"
            echo "has_activity=true" >> $GITHUB_OUTPUT
          fi

  project-manager-review:
    needs: check-activity
    if: needs.check-activity.outputs.has_activity == 'true'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install UV
        uses: astral-sh/setup-uv@v7

      - name: Set project manager prompt
        id: pm-prompt
        run: |
          cat >> $GITHUB_OUTPUT << 'EOF'
          PROMPT<<PROMPT_END
          You are a Project Manager for the kb-yaml-to-lens repository - a Python project that compiles Kibana dashboards from YAML to Lens format.

          # YOUR ROLE
          
          You are NOT a coder. You are a project manager who reviews the current state of the project and creates a prioritized list of actionable items that need maintainer attention.

          # IMPORTANT RULES
          
          1. **DO NOT** make code changes, create branches, or open pull requests
          2. **DO** analyze open issues, PRs, and recent activity
          3. **DO** identify blockers, stale items, and what needs maintainer decisions
          4. **DO** prioritize items by impact and urgency
          5. **BE SPECIFIC** - provide issue/PR numbers and concrete next steps
          6. You can search issues and PRs using available tools
          7. You can read the codebase to understand context
          8. You can run `git` commands to inspect repository state
          9. Focus on project health: Are issues being addressed? Are PRs stale? What's blocking progress?

          # YOUR TASK
          
          Analyze the project and create a structured report with these sections:

          ## 🚨 Urgent Items
          Items that are blocking progress or need immediate attention.

          ## 📋 Issues Requiring Decisions
          Open issues or PRs that need maintainer input to move forward.

          ## 🔄 Stale Items
          Issues or PRs that haven't seen activity in a while and may need a status update.

          ## ✅ Recent Progress
          Summary of what's been accomplished recently (merged PRs, closed issues).

          ## 💡 Suggested Next Steps
          Based on the current project state, what should maintainers focus on?

          ## 📊 Project Health Metrics
          - Open issues count
          - Open PRs count  
          - Average time to close issues/PRs
          - Issues/PRs with no recent activity (>14 days)

          # OUTPUT FORMAT
          
          Your response will be posted as a GitHub issue, so use clear markdown formatting with:
          - Issue/PR references using #number syntax
          - Bulleted lists for action items
          - Clear section headers
          - Checkboxes [ ] for actionable items
          - Emojis for visual organization

          # IMPORTANT
          
          Close any previous open project-manager issues before creating your report, as this represents the new daily status.

          PROMPT_END
          EOF

      - name: Setup GitHub MCP Server
        run: |
          mkdir -p /tmp/mcp-config
          cat > /tmp/mcp-config/mcp-servers.json << 'EOF'
          {
            "mcpServers": {
              "repository-summary": {
                "type": "http",
                "url": "https://agents-md-generator.fastmcp.app/mcp"
              },
              "github-research": {
                "type": "stdio",
                "command": "uvx",
                "args": [
                  "github-research-mcp"
                ],
                "env": {
                  "DISABLE_SUMMARIES": "true",
                  "GITHUB_PERSONAL_ACCESS_TOKEN": "${{ secrets.GITHUB_TOKEN }}"
                }
              }
            }
          }
          EOF

      - name: Close previous PM issue
        if: needs.check-activity.outputs.last_pm_issue != ''
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          LAST_ISSUE="${{ needs.check-activity.outputs.last_pm_issue }}"
          echo "Closing previous PM issue #$LAST_ISSUE"
          gh issue close "$LAST_ISSUE" --comment "Closing this PM report. New daily report has been generated."

      - name: Run Claude Project Manager
        id: claude
        uses: anthropics/claude-code-action@v1.0.23
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          
          additional_permissions: |
            actions: read
            issues: write

          prompt: ${{ steps.pm-prompt.outputs.PROMPT }}
          track_progress: true
          claude_args: |
            --allowed-tools mcp__repository-summary__generate_agents_md,mcp__github-research__search_issues,mcp__github-research__search_pull_requests,mcp__github-research__list_issues,mcp__github-research__list_pull_requests,mcp__github-research__get_issue,mcp__github-research__get_pull_request,Bash(git:*)
            --mcp-config /tmp/mcp-config/mcp-servers.json
```

## Setup Requirements

To use this workflow, you'll need to:

### 1. Create the Workflow File

Since GitHub blocks workflow creation via automation, **you'll need to manually create** `.github/workflows/claude-project-manager.yml` with the contents above.

### 2. Configure Secrets

The workflow requires the following secret to be set in your repository:

- `CLAUDE_CODE_OAUTH_TOKEN` - OAuth token for Claude Code action

You already have this configured for your other Claude workflows.

### 3. Label Setup

The workflow automatically adds a `project-manager` label to issues it creates. You may want to:

1. Create this label manually with a distinctive color (e.g., purple or orange)
2. Set a description like "Daily project management review from Claude"

### 4. Adjust Schedule (Optional)

The workflow runs daily at 9 AM UTC by default. To change this, modify the cron expression:
- `'0 9 * * *'` = 9 AM UTC daily
- `'0 13 * * *'` = 1 PM UTC (8 AM EST) daily  
- `'0 17 * * 1-5'` = 5 PM UTC Monday-Friday only

## How It Works

### Activity Detection Phase

1. Checks if there's an open `project-manager` issue
2. If yes, counts activity since that issue was created:
   - Git commits
   - New issues (excluding PM issues)
   - New pull requests
   - Merged pull requests
3. If total activity is less than 3 events, exits without creating a new issue
4. This prevents daily noise when the project is inactive

### Project Manager Phase

Only runs if activity is detected:

1. Closes any previous open PM issue
2. Runs Claude Code with project manager instructions
3. Claude analyzes:
   - Open issues and their status
   - Open PRs and their state
   - Recent commits and changes
   - Project documentation
4. Creates a new issue with structured report
5. Issue is automatically labeled `project-manager`

## What the PM Report Includes

- **Urgent Items**: Blockers needing immediate attention
- **Issues Requiring Decisions**: Items waiting on maintainer input
- **Stale Items**: Old issues/PRs needing updates
- **Recent Progress**: What's been accomplished
- **Suggested Next Steps**: Prioritized recommendations
- **Project Health Metrics**: Key statistics

## Benefits

1. **Reduces Maintainer Overhead**: Automated daily review of project status
2. **Prevents Items from Going Stale**: Flags issues/PRs needing attention
3. **Prioritizes Work**: Identifies most important items
4. **Tracks Progress**: Shows what's been accomplished
5. **Noise Reduction**: Only creates issues when there's actual activity
6. **Historical Record**: Creates a timeline of project status

## Testing

You can manually trigger the workflow to test it:

```bash
gh workflow run claude-project-manager.yml
```

Or use the GitHub UI: Actions → Claude Project Manager → Run workflow

## Customization

You can customize the behavior by:

1. **Activity Threshold**: Change `TOTAL_ACTIVITY -lt 3` to require more/fewer events
2. **Prompt**: Modify the PM prompt to focus on different aspects
3. **Schedule**: Adjust when the workflow runs
4. **Lookback Window**: Change `fetch-depth: 50` to look at more/less history

## Example Output

The workflow will create issues like:

```markdown
# Daily Project Status - December 20, 2025

## 🚨 Urgent Items

- [ ] #53 Create Project Manager workflow - This issue you're reading!
- [ ] #50 Remove poetry references - Blocking full migration to uv

## 📋 Issues Requiring Decisions

- [ ] #49 Move close to py-key-value for pyproject.toml
- [ ] #48 Review Documentation Accuracy
- [ ] #23 Add Kibana Dashboard Export Helper - Large scope, needs breakdown

## 🔄 Stale Items  

- [ ] #26 Issues with Claude and tools - No activity in 7 days

## ✅ Recent Progress

- Merged #42: Full migration to uv completed
- Merged #31: CLI with Kibana upload added
- Merged #32: ESQL query arrays implemented

## 💡 Suggested Next Steps

1. Complete uv migration cleanup (#50, #49)
2. Review and update documentation (#48)
3. Close or update inactive issues (#26)

## 📊 Project Health

- Open Issues: 26
- Open PRs: 2
- Avg Time to Close: ~2 days
- Stale (>14 days): 3 issues
```

## Notes

- The workflow respects the repository's existing Claude workflow patterns
- It uses the same MCP servers and tools
- It's designed to integrate seamlessly with your existing automation
- You can disable it at any time by removing the workflow file or disabling the workflow in GitHub
