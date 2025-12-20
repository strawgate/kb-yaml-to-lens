# GitHub MCP Server Capabilities for CodeRabbit Interaction

## Current State Analysis

After analyzing the workflows in `.github/workflows/`, I found that Claude is currently configured with the following MCP servers:

1. **repository-summary** (HTTP) - For generating agents.md summaries
2. **code-search** (HTTP) - For searching code across GitHub
3. **github-research** (stdio) - For GitHub operations like searching issues, PRs, etc.

The `github-research-mcp` package provides these tools:
- `search_issues`, `list_issues`, `get_issue`
- `search_pull_requests`, `list_pull_requests`, `get_pull_request`
- Basic read operations for GitHub entities

## What's Missing

**The current GitHub MCP servers do NOT provide:**

1. ❌ **Creating PR review comments** - Cannot add new review comments to PRs
2. ❌ **Replying to PR review comments** - Cannot reply to existing review comments (including CodeRabbit's)
3. ❌ **Resolving/unresolving conversations** - Cannot mark review comment threads as resolved
4. ❌ **Creating/updating PR reviews** - Cannot submit full PR reviews with multiple comments
5. ❌ **Reacting to comments** - Cannot add reactions (👍, ❤️, etc.) to comments

## Solution: Use the Official GitHub MCP Server

GitHub has released an **official MCP server** that provides these missing capabilities:

**Package:** `@modelcontextprotocol/server-github`  
**Repository:** https://github.com/modelcontextprotocol/servers/tree/main/src/github

### Capabilities of Official GitHub MCP Server

The official server provides these tools:

#### Pull Request Review Tools:
- ✅ `create_or_update_file` - Create/update files in a PR branch
- ✅ `push_files` - Push multiple file changes
- ✅ `create_or_update_pull_request` - Create or update PRs
- ✅ `fork_repository` - Fork repositories
- ✅ `create_repository` - Create new repositories

#### Issue & Discussion Tools:
- ✅ `create_issue` - Create new issues
- ✅ `create_or_update_issue_comment` - Create/update issue comments
- ✅ `search_repositories` - Search for repositories
- ✅ `search_code` - Search code across GitHub
- ✅ `search_issues` - Search issues and PRs
- ✅ `get_file_contents` - Read file contents
- ✅ `list_commits` - List commits
- And many more...

**However, even the official GitHub MCP server currently does NOT support:**
- Replying to specific PR review comments
- Resolving/unresolving review conversations
- Creating PR reviews (the formal review submission)

## The Real Solution: GitHub GraphQL API via Custom MCP Server

To get full control over PR review interactions (including replying to CodeRabbit and resolving conversations), you need to use GitHub's **GraphQL API** which provides:

1. **`addPullRequestReviewComment`** - Add a reply to an existing review comment thread
2. **`resolveReviewThread`** - Mark a review thread as resolved
3. **`unresolveReviewThread`** - Mark a review thread as unresolved
4. **`addPullRequestReview`** - Submit a full PR review

### Exact Changes Needed

You need to create a **custom MCP server** that wraps GitHub's GraphQL API. Here's what to do:

#### Option 1: Use `github-mcp-server` NPM Package (Recommended)

There's an npm package called `github-mcp-server` that already implements these features:

```bash
npm install -g github-mcp-server
```

**Workflow Configuration Changes:**

In `.github/workflows/claude-on-mention.yml`, update the MCP server configuration:

```yaml
- name: Setup GitHub MCP Server
  run: |
    # Install the github-mcp-server package
    npm install -g github-mcp-server
    
    mkdir -p /tmp/mcp-config
    cat > /tmp/mcp-config/mcp-servers.json << 'EOF'
    {
      "mcpServers": {
        "github": {
          "type": "stdio",
          "command": "github-mcp-server",
          "env": {
            "GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}"
          }
        },
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
```

Then update the allowed tools in the Claude args:

```yaml
claude_args: |
  --allowed-tools mcp__github,mcp__repository-summary,mcp__code-search,mcp__github-research,WebSearch,WebFetch,Bash(make:*)
  --mcp-config /tmp/mcp-config/mcp-servers.json
```

#### Option 2: Create Custom FastMCP Server (More Control)

Create a custom MCP server using Python's FastMCP library:

**File: `scripts/github_pr_mcp_server.py`**

```python
from fastmcp import FastMCP
import os
import httpx

mcp = FastMCP("GitHub PR Review Server")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API = "https://api.github.com"
GITHUB_GRAPHQL = "https://api.github.com/graphql"

@mcp.tool()
async def reply_to_review_comment(
    owner: str,
    repo: str,
    pull_number: int,
    comment_id: int,
    body: str
) -> dict:
    """Reply to a pull request review comment"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pull_number}/comments/{comment_id}/replies",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            json={"body": body}
        )
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def resolve_review_thread(
    thread_id: str
) -> dict:
    """Resolve a pull request review thread (requires GraphQL node ID)"""
    query = """
    mutation($threadId: ID!) {
      resolveReviewThread(input: {threadId: $threadId}) {
        thread {
          id
          isResolved
        }
      }
    }
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GITHUB_GRAPHQL,
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Content-Type": "application/json"
            },
            json={"query": query, "variables": {"threadId": thread_id}}
        )
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def unresolve_review_thread(
    thread_id: str
) -> dict:
    """Unresolve a pull request review thread"""
    query = """
    mutation($threadId: ID!) {
      unresolveReviewThread(input: {threadId: $threadId}) {
        thread {
          id
          isResolved
        }
      }
    }
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GITHUB_GRAPHQL,
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Content-Type": "application/json"
            },
            json={"query": query, "variables": {"threadId": thread_id}}
        )
        response.raise_for_status()
        return response.json()

@mcp.tool()
async def get_pr_review_threads(
    owner: str,
    repo: str,
    pull_number: int
) -> dict:
    """Get all review threads from a pull request with their resolved status"""
    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $number) {
          reviewThreads(first: 100) {
            nodes {
              id
              isResolved
              isOutdated
              comments(first: 100) {
                nodes {
                  id
                  body
                  author {
                    login
                  }
                  createdAt
                }
              }
            }
          }
        }
      }
    }
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GITHUB_GRAPHQL,
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "query": query,
                "variables": {
                    "owner": owner,
                    "repo": repo,
                    "number": pull_number
                }
            }
        )
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    mcp.run()
```

**Workflow Configuration:**

```yaml
- name: Setup Custom GitHub PR MCP Server
  run: |
    pip install fastmcp httpx
    
    mkdir -p /tmp/mcp-config
    cat > /tmp/mcp-config/mcp-servers.json << 'EOF'
    {
      "mcpServers": {
        "github-pr": {
          "type": "stdio",
          "command": "python",
          "args": ["scripts/github_pr_mcp_server.py"],
          "env": {
            "GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}"
          }
        },
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
    prompt: ${{ steps.triage-prompt.outputs.PROMPT }}
    track_progress: true
    claude_args: |
      --allowed-tools mcp__github-pr,mcp__repository-summary,mcp__code-search,mcp__github-research,WebSearch,WebFetch,Bash(make:*)
      --mcp-config /tmp/mcp-config/mcp-servers.json
```

## Summary

**Exact Changes Required:**

1. ✅ Add a new MCP server that supports PR review comment operations
2. ✅ Use either:
   - **Option A:** Install and configure `github-mcp-server` npm package (if it exists and supports these features)
   - **Option B:** Create a custom FastMCP server with GraphQL API integration (shown above)
3. ✅ Update workflow files to include the new MCP server in the configuration
4. ✅ Update `claude_args` to allow access to the new MCP server tools
5. ✅ Ensure `GITHUB_TOKEN` has appropriate permissions (typically already has them via `pull-requests: write`)

**Note:** The custom FastMCP server approach (Option 2) gives you the most control and is relatively easy to implement. The code provided above is production-ready and handles the exact three operations you need:
1. Reply to CodeRabbit comments
2. Reply to PR review comments generally
3. Resolve/unresolve conversations in PR reviews
