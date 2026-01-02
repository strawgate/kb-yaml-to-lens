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
- Instructions to poll for new comments using the `make gh-get-comments-since` command:

  ```bash
  make gh-get-comments-since OWNER REPO ISSUE_NUMBER TIMESTAMP AUTHOR
  ```

  This command:
  - **Automatically detects** whether the issue number is a pull request or issue
  - For pull requests:
    - Fetches both conversation comments AND inline review comments
    - Merges and sorts both types chronologically
  - For issues:
    - Only fetches conversation comments
  - Filters for comments created after the specified timestamp
  - Optionally filters for comments from a specific author
  - Returns matching comments in a format Claude can process
- Max 3 polling iterations to prevent infinite loops

This addresses issue #441 by allowing Claude to incorporate late-arriving feedback without requiring multiple @claude mentions.
