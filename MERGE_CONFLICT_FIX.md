# Fix for Merge Conflict Detection (Issue #140)

## Problem

The merge conflict detection workflow is broken because `git merge-tree --write-tree` fails when encountering unrelated histories, but the error message doesn't contain the string "CONFLICT", so the grep check incorrectly reports "No merge conflicts".

**Test showing the bug:**
```bash
$ git merge-tree --write-tree HEAD origin/main 2>&1
fatal: refusing to merge unrelated histories
[exit code: 128]

$ git merge-tree --write-tree HEAD origin/main 2>&1 | grep -q '^CONFLICT'
[no match - exit code 1]
```

Since the workflow runs with `bash -e`, the error is swallowed by the pipe, and the script continues with the wrong conclusion.

## Solution

The fix needs to be manually applied to `.github/workflows/claude-on-merge-conflict.yml` because GitHub App permissions prevent automated modification of workflow files.

### File to Edit

`.github/workflows/claude-on-merge-conflict.yml`

### Lines to Replace

**Replace lines 19-35** (the "Check for merge conflicts" step):

**OLD CODE:**
```yaml
      - name: Check for merge conflicts
        id: check
        run: |
          # Fetch the base branch
          git fetch origin ${{ github.event.pull_request.base.ref }}

          # Use modern git merge-tree with --write-tree to detect conflicts
          # This performs a three-way merge and outputs CONFLICT messages if conflicts exist
          echo "Checking for conflicts between HEAD and origin/${{ github.event.pull_request.base.ref }}"

          if git merge-tree --write-tree HEAD origin/${{ github.event.pull_request.base.ref }} 2>&1 | grep -q '^CONFLICT'; then
            echo "has_conflicts=true" >> $GITHUB_OUTPUT
            echo "✗ Merge conflicts detected"
          else
            echo "has_conflicts=false" >> $GITHUB_OUTPUT
            echo "✓ No merge conflicts"
          fi
```

**NEW CODE:**
```yaml
      - name: Check for merge conflicts
        id: check
        run: |
          # Fetch the base branch
          git fetch origin ${{ github.event.pull_request.base.ref }}

          echo "Checking for conflicts between HEAD and origin/${{ github.event.pull_request.base.ref }}"

          # Capture the merge-tree output and exit code
          set +e  # Temporarily disable exit on error
          merge_output=$(git merge-tree --write-tree HEAD origin/${{ github.event.pull_request.base.ref }} 2>&1)
          merge_exit_code=$?
          set -e  # Re-enable exit on error

          # Check for conflicts or unrelated histories
          if echo "$merge_output" | grep -q '^CONFLICT' || echo "$merge_output" | grep -q 'refusing to merge unrelated histories'; then
            echo "has_conflicts=true" >> $GITHUB_OUTPUT
            echo "✗ Merge conflicts detected"
          else
            echo "has_conflicts=false" >> $GITHUB_OUTPUT
            echo "✓ No merge conflicts"
          fi
```

## What Changed

1. **Capture output**: The merge-tree output is now captured in a variable instead of being piped directly to grep
2. **Disable exit-on-error**: Temporarily disable `set -e` to allow capturing the error message
3. **Check for both conditions**: The fix now checks for both "CONFLICT" markers AND the "refusing to merge unrelated histories" error message
4. **Re-enable exit-on-error**: After capturing the output, `set -e` is restored

## Manual Application

1. Open `.github/workflows/claude-on-merge-conflict.yml` in your editor
2. Find the "Check for merge conflicts" step (should be around lines 19-35)
3. Replace it with the new code above
4. Commit and push the changes directly to the main branch (or create a PR if preferred)

## Testing

After applying the fix, you can test it by:

1. Creating a branch with unrelated histories
2. Opening a PR from that branch
3. Verifying that the workflow correctly detects it as having conflicts

Related: #140
