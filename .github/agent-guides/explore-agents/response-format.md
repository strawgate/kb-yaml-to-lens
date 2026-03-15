# Explore Agent: Response Format

## Classifying findings

- **Bug**: The compiler produces incorrect JSON for a setting it claims to
  support — wrong field name, wrong value, wrong structure. The panel
  misbehaves or Kibana rejects it.
- **Gap**: Kibana supports a setting or field that the compiler has no config
  option for. Note it, but do NOT treat it as a bug.
- **Pass**: Compiled output works correctly in Kibana.

## When to create an issue

**If no bugs are found**, do not create an issue. No-op.

**If bugs or significant findings exist**, create one GitHub issue.

## Issue title format

`[WORKFLOW_TAG-KIBANA_VERSION] N bugs, M gaps`

Examples:
- `[explore-lens-xy-8.19.0] 3 bugs, 2 gaps`
- `[explore-lens-metric-9.3.0] 1 bug`
- `[explore-esql-pie-8.19.0] 4 gaps`

## Issue body structure

Use **collapsed sections** (`<details>`) for each category:

- **Compiler Bugs** — for each bug you MUST include:
  - The exact YAML config that reproduces the bug
  - What the compiler produces (relevant JSON snippet)
  - What Kibana expects (from manual panel export)
  - What happens (error message, wrong rendering, etc.)
- **Features Verified (passed)** — table of features tested with status
- **Feature Gaps (not in compiler)** — settings found in Kibana exports that
  the compiler doesn't support, with JSON snippets
- **Creative Exploration Results** — interesting combinations attempted

Top-level summary: total features tested, passed, bugs found, gaps
identified, version-specific notes.

## PR validation mode (comment-triggered workflows only)

When validating a PR, your deliverable is a **comment on the issue**
(not a new issue). Include:

- PR claim checklist with pass/fail per claim
- YAML configs used for each test (so bugs can be reproduced)
- For any failures: what the compiler produces vs what Kibana expects
- Explicit verdict on whether the PR fully satisfies its stated goal

## General rules

- Do not create branches or pull requests.
- Do not push code to any branch.
