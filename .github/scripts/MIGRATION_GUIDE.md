# Workflow Migration Guide

This guide shows how to update existing workflows to use the consolidated helper scripts.

## Why Migrate?

The workflow files currently contain duplicated bash logic and API calls. By migrating to helper scripts:

- **Reduce duplication**: Same logic used in multiple workflows is centralized
- **Improve testability**: Scripts can be tested independently
- **Simplify workflows**: Workflow files become more readable
- **Easier maintenance**: Fix bugs in one place instead of multiple workflows

## Migration Examples

### Example 1: Checking for Latest CodeRabbit Review

**Before** (in `claude-address-coderabbit-feedback.yml`):

```yaml
run: |
  set -euo pipefail
  CURRENT_REVIEW_ID="${{ github.event.review.id }}"
  LATEST_REVIEW=$(gh api graphql -f query='
    query($owner: String!, $repo: String!, $prNumber: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $prNumber) {
          reviews(last: 5, states: [CHANGES_REQUESTED, APPROVED, COMMENTED]) {
            nodes {
              databaseId
              createdAt
              author { login }
            }
          }
        }
      }
    }' -F owner="${{ github.repository_owner }}" \
       -F repo="${{ github.event.repository.name }}" \
       -F prNumber=${{ github.event.pull_request.number }} \
       --jq '.data.repository.pullRequest.reviews.nodes')

  LATEST_CODERABBIT_REVIEW=$(echo "$LATEST_REVIEW" | jq -r '
    map(select(.author.login == "coderabbitai[bot]"))
    | sort_by(.createdAt)
    | last // empty')
  LATEST_REVIEW_ID=$(echo "$LATEST_CODERABBIT_REVIEW" | jq -r '.databaseId // empty')
  if [ -n "$LATEST_REVIEW_ID" ] && [ "$LATEST_REVIEW_ID" != "$CURRENT_REVIEW_ID" ]; then
    echo "⚠️ A newer CodeRabbit review exists (ID: $LATEST_REVIEW_ID)"
    echo "⚠️ Current review ID: $CURRENT_REVIEW_ID"
    echo "⚠️ Skipping this run - the newer review will be or is being processed"
    exit 0
  fi
  echo "✅ This is the most recent CodeRabbit review, proceeding with work..."
```

**After** (using helper script):

```yaml
run: |
  .github/scripts/gh-check-latest-review.sh \
    "${{ github.repository_owner }}" \
    "${{ github.event.repository.name }}" \
    "${{ github.event.pull_request.number }}" \
    "coderabbitai[bot]" \
    "${{ github.event.review.id }}" || exit 0
  echo "✅ Proceeding with work..."
```

**Lines saved**: 32 → 8 (75% reduction)

---

### Example 2: Fetching Review Threads

**Before** (in `claude-address-coderabbit-feedback.yml`):

```yaml
run: |
  gh api graphql -f query='
    query($owner: String!, $repo: String!, $prNumber: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $prNumber) {
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
    }' -F owner="${{ github.repository_owner }}" \
       -F repo="${{ github.event.repository.name }}" \
       -F prNumber=${{ github.event.pull_request.number }} \
       --jq '.data.repository.pullRequest.reviewThreads.nodes'
```

**After** (using helper script):

```yaml
run: |
  THREADS=$(.github/scripts/gh-get-review-threads.sh \
    "${{ github.repository_owner }}" \
    "${{ github.event.repository.name }}" \
    "${{ github.event.pull_request.number }}" \
    "coderabbitai[bot]")
  echo "$THREADS" | jq .
```

**Lines saved**: 31 → 7 (77% reduction)

---

### Example 3: Resolving Review Threads

**Before** (in workflow prompts):

```yaml
prompt: |
  After successfully addressing a comment:
  ```bash
  gh api graphql -f query='
    mutation {
      resolveReviewThread(input: {threadId: "THREAD_ID"}) {
        thread { id isResolved }
      }
    }
  }'
  ```
```

**After** (using helper script):

```yaml
prompt: |
  After successfully addressing a comment:
  ```bash
  .github/scripts/gh-resolve-review-thread.sh "THREAD_ID"
  ```
```

---

### Example 4: Minimizing Outdated Comments (tidy-pr.yml)

**Before** (entire workflow logic):

```yaml
run: |-
  OWNER=$(echo "$REPOSITORY" | cut -d'/' -f1)
  REPO=$(echo "$REPOSITORY" | cut -d'/' -f2)
  echo "Fetching comments and reviews for PR #${PR_NUMBER}..."

  QUERY=$(cat <<'EOF'
  query($owner: String!, $repo: String!, $prNumber: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $prNumber) {
        comments(first: 100) {
          nodes {
            id
            author { login }
            createdAt
            isMinimized
          }
        }
        reviews(first: 100) {
          nodes {
            id
            author { login }
            createdAt
            comments(first: 100) {
              nodes {
                id
                author { login }
                createdAt
                isMinimized
              }
            }
          }
        }
      }
    }
  }
  EOF
  )

  RESPONSE=$(gh api graphql -f query="$QUERY" -f owner="$OWNER" -f repo="$REPO" -F prNumber="$PR_NUMBER")

  TO_MINIMIZE=$(echo "$RESPONSE" | jq -r '
    [
      (.data.repository.pullRequest.comments.nodes // []) +
      (.data.repository.pullRequest.reviews.nodes // [] | map(.comments.nodes // []) | add // []) +
      (.data.repository.pullRequest.reviews.nodes // [])
    ] | add
    | map(select(.isMinimized == false and .author != null))
    | group_by(.author.login)
    | map(sort_by(.createdAt) | .[:-1])
    | add // []
    | map(.id)
    | .[]
  ')

  MINIMIZED_COUNT=0
  for ID in $TO_MINIMIZE; do
    echo "Minimizing comment/review: $ID"
    MUTATION=$(cat <<'EOF'
    mutation($subjectId: ID!) {
      minimizeComment(input: {
        subjectId: $subjectId,
        classifier: OUTDATED
      }) {
        minimizedComment {
          isMinimized
        }
      }
    }
    EOF
    )
    gh api graphql -f query="$MUTATION" -f subjectId="$ID" > /dev/null
    MINIMIZED_COUNT=$((MINIMIZED_COUNT + 1))
  done
  echo "Successfully minimized $MINIMIZED_COUNT comments/reviews"
  echo "Kept the most recent comment/review from each user visible"
```

**After** (using helper script):

```yaml
run: |-
  OWNER=$(.github/scripts/gh-parse-repo.sh "${{ github.repository }}" owner)
  REPO=$(.github/scripts/gh-parse-repo.sh "${{ github.repository }}" repo)
  .github/scripts/gh-minimize-outdated-comments.sh "$OWNER" "$REPO" ${{ github.event.issue.number }}
```

**Lines saved**: 86 → 5 (94% reduction)

---

### Example 5: Getting Comments Since Timestamp

**Before** (new feature in issue #441):

```yaml
run: |
  gh api "/repos/${{ github.repository }}/issues/${{ github.event.issue.number }}/comments?since=${{ github.event.comment.created_at }}" \
    --jq 'map(select(.user.login == "${{ github.event.comment.user.login }}"))'
```

**After** (using helper script):

```yaml
run: |
  .github/scripts/gh-get-comments-since.sh \
    "${{ github.repository_owner }}" \
    "${{ github.event.repository.name }}" \
    "${{ github.event.issue.number }}" \
    "${{ github.event.comment.created_at }}" \
    "${{ github.event.comment.user.login }}"
```

---

## How to Request Changes

Since Claude cannot modify workflow files (GitHub App permissions), use @copilot to make changes.

### Template for @copilot Requests

```markdown
@copilot In `.github/workflows/[WORKFLOW_FILE].yml`, replace lines [START]-[END] with:

[PASTE THE "AFTER" CODE FROM EXAMPLES ABOVE]

This change consolidates duplicated bash logic into a reusable helper script located in `.github/scripts/`.
```

### Example Request

```markdown
@copilot In `.github/workflows/claude-address-coderabbit-feedback.yml`, replace lines 45-78 with:

```yaml
run: |
  .github/scripts/gh-check-latest-review.sh \
    "${{ github.repository_owner }}" \
    "${{ github.event.repository.name }}" \
    "${{ github.event.pull_request.number }}" \
    "coderabbitai[bot]" \
    "${{ github.event.review.id }}" || exit 0
  echo "✅ Proceeding with work..."
```

This change consolidates the "check for latest review" logic into a reusable helper script.
```

---

## Testing After Migration

After migrating a workflow:

1. **Test locally** (if possible):
   ```bash
   export GITHUB_TOKEN="your_token"
   .github/scripts/gh-check-latest-review.sh strawgate kb-yaml-to-lens 426 "coderabbitai[bot]" 12345
   ```

2. **Test in a PR**: Create a test PR and trigger the workflow

3. **Verify output**: Check that the workflow produces the same results as before

---

## Workflows to Migrate

| Workflow | Lines to Replace | Potential Helper |
|----------|-----------------|------------------|
| `claude-address-coderabbit-feedback.yml` | Lines 45-78 (latest review check) | `gh-check-latest-review.sh` |
| `claude-address-coderabbit-feedback.yml` | Lines 82-109 (fetch review threads) | `gh-get-review-threads.sh` |
| `claude-address-coderabbit-feedback.yml` | Lines 124-184 (check for new feedback) | `gh-check-latest-review.sh` + `gh-get-review-threads.sh` |
| `claude-address-coderabbit-feedback.yml` | Lines 190-197 (resolve threads) | `gh-resolve-review-thread.sh` |
| `tidy-pr.yml` | Lines 26-110 (entire minimization logic) | `gh-minimize-outdated-comments.sh` + `gh-parse-repo.sh` |
| `claude-on-mention-assist.yml` | Prompts mentioning thread resolution | Update prompt to reference `gh-resolve-review-thread.sh` |
| `claude-on-mention-create-issues.yml` | Prompts mentioning thread resolution | Update prompt to reference `gh-resolve-review-thread.sh` |

---

## Benefits Summary

| Metric | Before Migration | After Migration | Improvement |
|--------|-----------------|-----------------|-------------|
| Total lines of bash in workflows | ~200 | ~30 | 85% reduction |
| Duplicate GraphQL queries | 5+ copies | 0 (centralized) | 100% deduplication |
| Testable scripts | 0 | 7 | ∞% |
| Workflow readability | Low | High | Significant |
