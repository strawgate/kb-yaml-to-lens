# Resolving PR Review Threads
You have access to resolve review threads in pull requests using the GitHub GraphQL API via `gh api`.

**IMPORTANT**: You should ONLY resolve threads after making code changes that address the feedback. Do not resolve threads without fixing the underlying issue.

To get review threads and their IDs:
```bash
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      pullRequest(number: PR_NUMBER) {
        reviewThreads(first: 100) {
          nodes { id isResolved path line
            comments(first: 10) { nodes { body author { login } } }
          }
        }
      }
    }
  }' -f owner=OWNER -f name=REPO -F number=PR_NUMBER
```

To resolve a review thread (after addressing the feedback):
```bash
gh api graphql -f query='
  mutation {
    resolveReviewThread(input: {threadId: "THREAD_ID"}) {
      thread { id isResolved }
    }
  }'
```

When working with CodeRabbit or other review feedback:
1. Make the necessary code changes to address the feedback
2. Use `gh api graphql` to fetch review threads and identify which ones are addressed
3. Use `gh api graphql` with resolveReviewThread mutation to mark resolved conversations
