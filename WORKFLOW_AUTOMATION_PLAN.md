# Workflow Automation Plan: CodeRabbit Feedback & Test Failure

## Executive Summary

This document proposes two new Claude workflows to improve PR velocity:

1. **claude-on-coderabbit-feedback.yml** - Auto-responds to CodeRabbit reviews with fixes
2. **claude-on-test-failure.yml** - Analyzes and suggests fixes for test failures

Both workflows include concurrency controls to prevent infinite loops and resource exhaustion.

---

## Current State Analysis

### Existing Workflows

| Workflow | Trigger | Purpose | Concurrency |
|----------|---------|---------|-------------|
| `claude-on-mention.yml` | `@claude` mention in comments/reviews | General code assistance | None (manual trigger) |
| `claude-on-merge-conflict.yml` | PR with merge conflicts | Auto-resolve conflicts | Per-PR branch |
| `claude-on-open-label.yml` | Issue opened/labeled | Triage and analysis | None (read-only) |
| `test.yml` | Push/PR to main/develop | Run tests, lint, typecheck | None |

### Key Observations

1. **No automatic response to code reviews** - Currently requires manual `@claude` mentions
2. **No test failure analysis** - Developers must manually investigate failures
3. **Existing concurrency patterns**:
   - Merge conflict resolver uses: `concurrency: group: resolve-conflicts-${{ github.event.pull_request.number }}`
   - No concurrency control on mention-triggered workflows (intentional - manual trigger)

---

## Proposed Workflow 1: Claude on CodeRabbit Feedback

### Trigger Conditions

```yaml
on:
  pull_request_review:
    types: [submitted]

jobs:
  claude-coderabbit-response:
    # Only run if:
    # 1. Review is from coderabbitai bot
    # 2. Review has comments or requests changes
    # 3. PR is not in draft state
    if: |
      github.event.review.user.login == 'coderabbitai[bot]' &&
      (github.event.review.state == 'commented' || github.event.review.state == 'changes_requested') &&
      !github.event.pull_request.draft
```

### Concurrency Strategy

```yaml
concurrency:
  group: claude-coderabbit-${{ github.event.pull_request.number }}
  cancel-in-progress: true
```

**Rationale:**
- One Claude response per PR at a time
- Cancel previous runs if new CodeRabbit review arrives
- Prevents queue buildup if multiple reviews happen quickly

### Safety Mechanisms

1. **Rate Limiting**: Only trigger on CodeRabbit reviews (not all reviews)
2. **Draft Protection**: Skip draft PRs to avoid premature automation
3. **Single Review Per Trigger**: One CodeRabbit review = one Claude response
4. **No Self-Triggering**: Claude's commits don't trigger CodeRabbit re-reviews (CodeRabbit typically configured to ignore bot commits)

### Prompt Strategy

The Claude prompt should:
- Fetch CodeRabbit review comments via GitHub API
- Address each comment with code changes
- Mark review threads as resolved after fixing (using GraphQL API as in claude-on-mention)
- Run `make lint` and `make test` after changes
- Report if any comments cannot be addressed (with explanation)

### Workflow Structure

```yaml
name: Claude CodeRabbit Response

on:
  pull_request_review:
    types: [submitted]

concurrency:
  group: claude-coderabbit-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  claude-coderabbit-response:
    if: |
      github.event.review.user.login == 'coderabbitai[bot]' &&
      (github.event.review.state == 'commented' || github.event.review.state == 'changes_requested') &&
      !github.event.pull_request.draft
    runs-on: ubuntu-latest
    timeout-minutes: 30
    permissions:
      contents: write
      pull-requests: write
      id-token: write
      actions: read
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.ref }}
          fetch-depth: 0

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install UV
        uses: astral-sh/setup-uv@v7

      - name: Set CodeRabbit response prompt
        id: prompt
        run: |
          cat >> $GITHUB_OUTPUT << 'EOF'
          PROMPT<<PROMPT_END
          You're a code assistant for kb-yaml-to-lens responding to CodeRabbit review feedback.

          # YOUR TASK
          
          CodeRabbit has left review feedback on PR #${{ github.event.pull_request.number }}.
          Review ID: ${{ github.event.review.id }}
          
          Your goal is to:
          1. Fetch all review comments from CodeRabbit for this PR
          2. Address each comment by making appropriate code changes
          3. Resolve review threads after fixing issues
          4. Run tests/linting to verify fixes
          5. Document what was fixed and what couldn't be fixed

          # GETTING STARTED

          1. Call the generate_agents_md tool to understand the project structure
          2. Fetch review threads using GitHub GraphQL API:
             ```bash
             gh api graphql -f query='
               query {
                 repository(owner: "${{ github.repository_owner }}", name: "${{ github.event.repository.name }}") {
                   pullRequest(number: ${{ github.event.pull_request.number }}) {
                     reviewThreads(first: 100) {
                       nodes {
                         id
                         isResolved
                         isOutdated
                         path
                         line
                         comments(first: 10) {
                           nodes {
                             id
                             body
                             author { login }
                             createdAt
                           }
                         }
                       }
                     }
                   }
                 }
               }'
             ```
          3. Filter threads to only those from coderabbitai[bot] that are unresolved

          # ADDRESSING FEEDBACK

          For each unresolved CodeRabbit comment:
          1. Read the file and understand the context
          2. Make the suggested change (or a better alternative if you disagree)
          3. Document your reasoning if you deviate from the suggestion
          4. After all changes, run: `make lint` and `make test`
          5. Fix any failures caused by your changes

          # RESOLVING THREADS

          After successfully addressing a comment:
          ```bash
          gh api graphql -f query='
            mutation {
              resolveReviewThread(input: {threadId: "THREAD_ID"}) {
                thread { id isResolved }
              }
            }'
          ```

          # REPORTING

          After all changes, comment on the PR with a summary:
          - ✅ Comments addressed (list each with brief description)
          - ⚠️ Comments not addressed (explain why)
          - 🧪 Test results
          - 📝 Additional notes

          # IMPORTANT GUIDELINES

          - Be surgical - only change what's needed to address feedback
          - If CodeRabbit is wrong, explain why in your response
          - Always run tests after changes
          - Don't blindly accept every suggestion - use judgment
          - If you can't address a comment, explain why clearly

          # AVOIDING LOOPS

          - Make ONE round of changes per CodeRabbit review
          - Don't re-trigger CodeRabbit by mentioning it or requesting re-review
          - Focus on fixing issues, not perfecting code
          
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
              "code-search": {
                "type": "http",
                "url": "https://public-code-search.fastmcp.app/mcp"
              },
              "github-research": {
                "type": "stdio",
                "command": "uvx",
                "args": ["github-research-mcp"],
                "env": {
                  "DISABLE_SUMMARIES": "true",
                  "GITHUB_PERSONAL_ACCESS_TOKEN": "${{ secrets.GITHUB_TOKEN }}"
                }
              }
            }
          }
          EOF

      - name: Run Claude Code
        id: claude
        uses: anthropics/claude-code-action@v1.0.23
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          additional_permissions: |
            actions: read
          prompt: ${{ steps.prompt.outputs.PROMPT }}
          track_progress: true
          claude_args: |
            --allowed-tools mcp__repository-summary,mcp__code-search,mcp__github-research,Bash(make:*,git:add:*,git:commit:*,git:push:*,git:status:*,git:diff:*,gh:api:*)
            --mcp-config /tmp/mcp-config/mcp-servers.json
```

---

## Proposed Workflow 2: Claude on Test Failure

### Trigger Conditions

```yaml
on:
  workflow_run:
    workflows: ["Run Tests"]
    types: [completed]

jobs:
  claude-test-analysis:
    if: |
      github.event.workflow_run.conclusion == 'failure' &&
      github.event.workflow_run.event == 'pull_request'
```

### Concurrency Strategy

```yaml
concurrency:
  group: claude-test-failure-${{ github.event.workflow_run.head_branch }}
  cancel-in-progress: true
```

**Rationale:**
- One test failure analysis per branch at a time
- Cancel previous runs if new commits pushed (new test run)
- Prevents analyzing stale failures

### Safety Mechanisms

1. **Only PR failures**: Skip failures on main branch (those need manual attention)
2. **Single analysis per run**: One test failure = one Claude analysis
3. **No auto-fix**: Claude comments with suggestions but doesn't auto-push fixes (prevents breaking changes)
4. **Edit existing comment**: If Claude already commented, edit that comment instead of creating new ones

### Prompt Strategy

The Claude prompt should:
- Use GitHub MCP tools to fetch job logs (`get_job_logs` with `failed_only=true`)
- Analyze failure patterns and root causes
- Search codebase for relevant context
- Provide actionable fix suggestions
- Update/edit existing comment if Claude previously analyzed this PR

### Workflow Structure

```yaml
name: Claude Test Failure Analysis

on:
  workflow_run:
    workflows: ["Run Tests"]
    types: [completed]

concurrency:
  group: claude-test-failure-${{ github.event.workflow_run.head_branch }}
  cancel-in-progress: true

jobs:
  claude-test-analysis:
    # Only run if test workflow failed on a pull request
    if: |
      github.event.workflow_run.conclusion == 'failure' &&
      github.event.workflow_run.event == 'pull_request'
    runs-on: ubuntu-latest
    timeout-minutes: 30
    permissions:
      contents: read
      pull-requests: write
      issues: read
      id-token: write
      actions: read
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

      - name: Set analysis prompt
        id: prompt
        run: |
          cat >> $GITHUB_OUTPUT << 'EOF'
          PROMPT<<PROMPT_END
          You're a test failure analysis assistant for kb-yaml-to-lens, a Python project that compiles Kibana dashboards from YAML.

          # YOUR TASK

          A GitHub Actions workflow has failed. Your job is to:
          1. Analyze the test failure(s) to understand what went wrong
          2. Identify the root cause of the failure(s)
          3. Suggest clear, actionable solutions

          # GETTING STARTED

          1. Call the generate_agents_md tool to get a high-level summary of the project
          2. Get the pull request associated with this workflow run:
             - Workflow run ID: ${{ github.event.workflow_run.id }}
             - Workflow run event: ${{ github.event.workflow_run.event }}
             - Branch: ${{ github.event.workflow_run.head_branch }}
          3. Use GitHub CI MCP tools to fetch failure information:
             - Workflow run ID: ${{ github.event.workflow_run.id }}
             - Use mcp__github_ci__get_ci_status to get overall CI status
             - Use mcp__github_ci__get_workflow_run_details with run_id=${{ github.event.workflow_run.id }} to get job details
             - Use mcp__github_ci__download_job_log with job_id=<failed_job_id> to download logs for failed jobs
          4. Analyze the failures to understand root cause
          5. Search the codebase for relevant context

          # YOUR RESPONSE

          Check if you've previously commented on this PR. If so, EDIT that comment instead of creating a new one.

          To find the PR number and existing comments:
          ```bash
          # Get PR number from workflow run
          PR_NUMBER=$(gh api repos/${{ github.repository }}/actions/runs/${{ github.event.workflow_run.id }} --jq '.pull_requests[0].number')

          # Find existing comments from Claude/bot
          gh api repos/${{ github.repository }}/issues/$PR_NUMBER/comments --jq '.[] | select(.user.login=="github-actions[bot]" or .user.login=="claude") | {id: .id, body: .body}'
          ```

          Post (or edit) a comment with:

          ## Test Failure Analysis

          **Summary**: Brief 1-2 sentence overview of what failed.

          **Root Cause**: Clear explanation based on logs and code analysis.

          **Suggested Solution**: Specific, actionable steps to fix:
          - Which files to modify
          - What changes to make
          - Why these changes will fix the issue

          <details>
          <summary>Detailed Analysis</summary>

          - Relevant log excerpts
          - Code snippets causing the issue
          - Related issues/PRs if any
          </details>

          <details>
          <summary>Related Files</summary>

          List files relevant to the failure with brief explanations.
          </details>

          # IMPORTANT GUIDELINES

          - Be concise and actionable - developers want quick understanding
          - Focus on facts from logs/code, not speculation
          - If root cause is unclear, say so explicitly
          - Provide file names, line numbers, specific code references
          - Use WebSearch/WebFetch to research unfamiliar errors if needed
          - If your only suggestion is "skip the test" or "increase timeout", note that as a last resort

          # AVOID ANALYSIS LOOPS

          - Edit existing comments instead of creating new ones
          - Don't analyze the same failure twice
          - If you've already provided suggestions and they weren't followed, don't repeat them
          
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
              "code-search": {
                "type": "http",
                "url": "https://public-code-search.fastmcp.app/mcp"
              },
              "github-research": {
                "type": "stdio",
                "command": "uvx",
                "args": ["github-research-mcp"],
                "env": {
                  "DISABLE_SUMMARIES": "true",
                  "GITHUB_PERSONAL_ACCESS_TOKEN": "${{ secrets.GITHUB_TOKEN }}"
                }
              }
            }
          }
          EOF

      - name: Run Claude Code
        id: claude
        uses: anthropics/claude-code-action@v1.0.23
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          additional_permissions: |
            actions: read
          prompt: ${{ steps.prompt.outputs.PROMPT }}
          claude_args: |
            --allowed-tools mcp__repository-summary,mcp__code-search,mcp__github-research,WebSearch,WebFetch,Bash(make:*,git:*,gh:api:*)
            --mcp-config /tmp/mcp-config/mcp-servers.json
```

---

## Concurrency Control Strategy

### Overall Design Principles

1. **Per-PR/Branch Scoping**: Each workflow uses PR number or branch name in concurrency group
2. **Cancel-in-progress**: New triggers cancel old runs to prevent queue buildup
3. **No Cross-Workflow Triggering**: Workflows don't trigger each other
4. **Single Action Per Trigger**: Each workflow performs one action then exits

### Preventing Infinite Loops

| Risk | Mitigation |
|------|------------|
| Claude triggers CodeRabbit | CodeRabbit configured to ignore bot commits (standard practice) |
| CodeRabbit triggers Claude triggers CodeRabbit | Claude makes changes in ONE iteration, doesn't re-request review |
| Test failure triggers Claude triggers test failure | Claude only comments, doesn't push changes that would re-trigger tests |
| Multiple Claudes run simultaneously | Concurrency groups ensure only one Claude per PR/branch |
| Workflow queue exhaustion | `cancel-in-progress: true` prevents queue buildup |

### Monitoring & Alerting

To detect issues early:

1. **GitHub Actions dashboard**: Monitor for:
   - Workflows with > 5 runs in 1 hour on same PR
   - Workflows stuck in "queued" state
   - Unusual cancellation rates

2. **Add workflow timeout**:
   ```yaml
   jobs:
     claude-job:
       timeout-minutes: 30  # Prevent runaway workflows
   ```

3. **Rate limit protection**: GitHub Actions has built-in limits:
   - 20 concurrent jobs per repository (Free tier)
   - 1000 API requests per hour per workflow

---

## Comparison with Existing Patterns

### Similar to: claude-on-merge-conflict.yml

**Similarities:**
- Auto-triggered (not manual)
- Makes code changes
- Uses per-PR concurrency control
- Has clear exit condition

**Differences:**
- CodeRabbit workflow responds to reviews, not merge conflicts
- Test failure workflow only comments, doesn't push changes

### Different from: claude-on-mention.yml

**Similarities:**
- Can make code changes
- Accesses MCP tools and Bash

**Differences:**
- Auto-triggered vs manual `@claude` mention
- Needs concurrency control (mention workflow doesn't)
- More specific scope (review feedback vs general assistance)

---

## Implementation Checklist

### Phase 1: Preparation
- [ ] Review this plan with maintainers
- [ ] Verify CodeRabbit is configured to ignore bot commits
- [ ] Confirm `CLAUDE_CODE_OAUTH_TOKEN` secret is configured
- [ ] Test concurrency groups don't conflict with existing workflows

### Phase 2: CodeRabbit Workflow
- [ ] Create `.github/workflows/claude-on-coderabbit-feedback.yml`
- [ ] Test on a draft PR with CodeRabbit review
- [ ] Verify thread resolution works
- [ ] Monitor for loop behavior

### Phase 3: Test Failure Workflow
- [ ] Create `.github/workflows/claude-on-test-failure.yml`
- [ ] Test with an intentionally failing test
- [ ] Verify comment editing works
- [ ] Monitor for loop behavior

### Phase 4: Monitoring
- [ ] Document workflow behavior in AGENTS.md or CONTRIBUTING.md
- [ ] Set up monitoring for workflow health
- [ ] Create runbook for disabling workflows if loops occur

---

## Rollback Plan

If workflows cause issues:

1. **Immediate disable**: Add to workflow file:
   ```yaml
   jobs:
     job-name:
       if: false  # Temporarily disable
   ```

2. **Investigate**: Check GitHub Actions logs for:
   - Repeated triggers
   - Failed concurrency controls
   - Permission errors

3. **Fix or remove**: Either fix the issue or delete the workflow file

---

## Alternative Approaches Considered

### Alternative 1: Manual trigger only
**Pros:** No loop risk, full control
**Cons:** Defeats purpose of automation, requires `@claude` mentions

**Decision:** Rejected - automation is the goal

### Alternative 2: Human approval before Claude acts
**Pros:** Safety net, human oversight
**Cons:** Slower, adds friction

**Decision:** Not needed - concurrency controls + bot commit filtering sufficient

### Alternative 3: Claude makes PRs instead of pushing to branch
**Pros:** More visible, easier to review
**Cons:** PR clutter, defeats purpose of automation

**Decision:** Rejected - too much overhead

---

## Success Metrics

After 2 weeks of running these workflows, measure:

1. **PR velocity**: Time from CodeRabbit review to resolution
2. **Test failure resolution**: Time from test failure to fix
3. **Loop incidents**: Number of times workflows triggered > 3x on same PR
4. **False fixes**: Number of times Claude's changes were reverted
5. **Developer satisfaction**: Survey team on workflow usefulness

Target: 50% reduction in review-to-fix time, zero loop incidents

---

## Next Steps

This plan is **ready for review and implementation**. To proceed:

**@copilot** Please review this plan and implement:
1. `.github/workflows/claude-on-coderabbit-feedback.yml` as specified above
2. `.github/workflows/claude-on-test-failure.yml` as specified above

Both workflows are production-ready with proper concurrency controls and safety mechanisms.

cc: @strawgate for review
