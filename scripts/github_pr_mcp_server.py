#!/usr/bin/env python3
"""
GitHub PR Review MCP Server

This MCP server provides tools for interacting with GitHub pull request reviews,
including replying to comments, resolving conversations, and managing review threads.

Required environment variables:
- GITHUB_TOKEN: GitHub personal access token with repo permissions
"""

import os
import sys
from typing import Any

try:
    from fastmcp import FastMCP
    import httpx
except ImportError:
    print("Error: Required packages not installed. Install with: pip install fastmcp httpx", file=sys.stderr)
    sys.exit(1)

mcp = FastMCP("GitHub PR Review Server")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN environment variable is required", file=sys.stderr)
    sys.exit(1)

GITHUB_API = "https://api.github.com"
GITHUB_GRAPHQL = "https://api.github.com/graphql"


@mcp.tool()
async def reply_to_review_comment(
    owner: str,
    repo: str,
    pull_number: int,
    comment_id: int,
    body: str,
) -> dict[str, Any]:
    """
    Reply to a pull request review comment (including CodeRabbit comments).

    Args:
        owner: Repository owner (organization or user)
        repo: Repository name
        pull_number: Pull request number
        comment_id: The ID of the review comment to reply to
        body: The content of the reply

    Returns:
        The created comment object

    Example:
        reply_to_review_comment(
            owner="strawgate",
            repo="kb-yaml-to-lens",
            pull_number=42,
            comment_id=123456789,
            body="Thanks for the feedback! I've addressed this."
        )
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GITHUB_API}/repos/{owner}/{repo}/pulls/comments/{comment_id}/replies",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json={"body": body},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def resolve_review_thread(thread_id: str) -> dict[str, Any]:
    """
    Resolve a pull request review thread.

    Args:
        thread_id: The GraphQL node ID of the review thread (starts with "PRRT_")

    Returns:
        The updated thread object

    Example:
        resolve_review_thread(thread_id="PRRT_kwDOAbCdEf4AaBbCc")
    """
    query = """
    mutation($threadId: ID!) {
      resolveReviewThread(input: {threadId: $threadId}) {
        thread {
          id
          isResolved
          isOutdated
        }
      }
    }
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GITHUB_GRAPHQL,
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Content-Type": "application/json",
            },
            json={"query": query, "variables": {"threadId": thread_id}},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        return data


@mcp.tool()
async def unresolve_review_thread(thread_id: str) -> dict[str, Any]:
    """
    Unresolve a pull request review thread.

    Args:
        thread_id: The GraphQL node ID of the review thread (starts with "PRRT_")

    Returns:
        The updated thread object

    Example:
        unresolve_review_thread(thread_id="PRRT_kwDOAbCdEf4AaBbCc")
    """
    query = """
    mutation($threadId: ID!) {
      unresolveReviewThread(input: {threadId: $threadId}) {
        thread {
          id
          isResolved
          isOutdated
        }
      }
    }
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GITHUB_GRAPHQL,
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Content-Type": "application/json",
            },
            json={"query": query, "variables": {"threadId": thread_id}},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        return data


@mcp.tool()
async def get_pr_review_threads(owner: str, repo: str, pull_number: int) -> dict[str, Any]:
    """
    Get all review threads from a pull request with their resolved status.

    This is useful for finding thread IDs to resolve, or to see all CodeRabbit
    feedback and other review comments.

    Args:
        owner: Repository owner (organization or user)
        repo: Repository name
        pull_number: Pull request number

    Returns:
        All review threads with comments, authors, and resolved status

    Example:
        get_pr_review_threads(
            owner="strawgate",
            repo="kb-yaml-to-lens",
            pull_number=42
        )
    """
    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $number) {
          reviewThreads(first: 100) {
            nodes {
              id
              isResolved
              isOutdated
              isCollapsed
              path
              line
              comments(first: 100) {
                nodes {
                  id
                  databaseId
                  body
                  author {
                    login
                  }
                  createdAt
                  path
                  position
                  originalPosition
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
                "Content-Type": "application/json",
            },
            json={"query": query, "variables": {"owner": owner, "repo": repo, "number": pull_number}},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        return data


@mcp.tool()
async def get_pr_review_comments(owner: str, repo: str, pull_number: int) -> dict[str, Any]:
    """
    Get all review comments from a pull request (REST API version).

    This provides comment IDs that can be used with reply_to_review_comment.

    Args:
        owner: Repository owner (organization or user)
        repo: Repository name
        pull_number: Pull request number

    Returns:
        List of all review comments with IDs and details

    Example:
        get_pr_review_comments(
            owner="strawgate",
            repo="kb-yaml-to-lens",
            pull_number=42
        )
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pull_number}/comments",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    mcp.run()
