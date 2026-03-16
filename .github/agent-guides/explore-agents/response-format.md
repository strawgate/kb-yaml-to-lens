# Explore Agent: Response Format

## Report structure

Your report MUST have results from **both** verification jobs. If you only
completed one, say so explicitly and explain why (e.g., "Job 2 not completed:
ran out of time after Job 1 found 3 bugs").

### Required sections

1. **Summary** — one paragraph: how many features tested, bugs found, gaps found
2. **Job 1: Compiler → Kibana** — table of features tested via YAML → compile → import → verify
3. **Job 2: Kibana → Compiler comparison** — table of settings created in Kibana UI → exported → compared to compiler
4. **Compiler Bugs** (if any) — detailed bug reports with YAML, JSON, and Kibana evidence
5. **Feature Gaps** (if any) — settings Kibana supports that the compiler doesn't
6. **Features Verified** — summary of what passed

## Classifying findings

- **Bug**: The compiler produces incorrect JSON for a setting it claims to
  support — wrong field name, wrong value, wrong structure. The panel
  misbehaves or Kibana rejects it.
- **Gap**: Kibana supports a setting or field that the compiler has no config
  option for. Note it, but do NOT treat it as a bug.
- **Pass**: Compiled output works correctly in Kibana.

## When to create an issue

**If no bugs or gaps are found**, do not create an issue. Use the `noop` tool
with a message like "All features verified, 0 bugs, 0 gaps."

**If bugs or significant findings exist**, create one GitHub issue.

## Issue title

The workflow auto-prefixes the title. Just provide the summary:

`N bugs, M gaps`

Examples: `3 bugs, 2 gaps` · `1 bug` · `0 bugs, 4 gaps`

## Issue body structure

```markdown
## Summary
Tested N features against Kibana X.Y.Z. Found B bugs and G gaps.

## Job 1: Compiler → Kibana

| Feature | YAML | Panel renders? | Editor correct? | Status |
|---------|------|---------------|-----------------|--------|
| ... | ... | ... | ... | PASS/BUG |

## Job 2: Kibana → Compiler comparison

| Setting created in Kibana | Kibana JSON field | Compiler emits? | Correct? | Status |
|--------------------------|-------------------|-----------------|----------|--------|
| ... | ... | ... | ... | PASS/GAP |

<details>
<summary>Compiler Bugs</summary>

### Bug 1: [title]
- **YAML:** (the config that reproduces it)
- **Compiler output:** (relevant JSON snippet)
- **Kibana behavior:** (what happens — error message, wrong rendering)
- **Expected:** (what Kibana needs)
- **Root cause:** (file and line if identified)

</details>

<details>
<summary>Feature Gaps</summary>

### Gap 1: [title]
- **Kibana JSON:** (the field from exported JSON)
- **Compiler:** (no corresponding config option)

</details>

<details>
<summary>Features Verified (passed)</summary>

| Feature | Status | Notes |
|---------|--------|-------|
| ... | PASS | ... |

</details>
```

## PR validation mode

When validating a PR (triggered by a comment), post a **comment on the PR**
(not a new issue). Include:

- PR claim checklist with pass/fail per claim
- Job 1 and Job 2 tables (at minimum Job 1 for the PR's claimed features)
- For failures: YAML, compiler output, and Kibana evidence
- Explicit verdict: does the PR fully satisfy its stated goal?

## General rules

- Do not create branches or pull requests.
- Do not push code to any branch.
- Every finding MUST be backed by Kibana evidence, not just code reading.
