# Updated Workflow Files

This directory contains updated workflow files that implement the comment-checking feature requested in issue #441.

## What Changed

Both workflow files now include instructions for Claude to check for new comments before finishing:

### `claude-on-mention-assist.yml`
- Added step 6 in the "YOUR TASK" section
- Instructs Claude to check for new comments created after the workflow started
- Provides bash script example using GitHub API and jq
- Includes max 3 checks limit to prevent infinite loops

### `claude-on-mention-create-issues.yml`
- Added "BEFORE FINISHING" section
- Same comment-checking logic as above
- Ensures issue creation workflows also incorporate late-arriving feedback

## How to Apply These Changes

Since Claude cannot directly modify workflow files (GitHub App permissions restriction), you need to manually copy these files:

```bash
# From the repository root
cp github/workflows/claude-on-mention-assist.yml .github/workflows/
cp github/workflows/claude-on-mention-create-issues.yml .github/workflows/

# Commit the changes
git add .github/workflows/
git commit -m "Add comment-checking feature to Claude workflows"
git push
```

## Testing the Feature

After merging, test the feature by:

1. Creating a test issue
2. Mention @claude with a simple request
3. While Claude is working (within the first minute or so), add a follow-up comment
4. Claude should detect the new comment and incorporate the feedback before finishing

## How It Works

The workflows now include:
- Workflow start time tracking using `${{ github.event.comment.created_at || github.event.review.submitted_at }}`
- Instructions to poll GitHub API for new comments using `gh api` and `jq`
- Filtering for comments from the trigger user only
- Timestamp comparison to find comments created after the workflow started
- Max 3 polling iterations to prevent infinite loops

This addresses issue #441 by allowing Claude to incorporate late-arriving feedback without requiring multiple @claude mentions.
