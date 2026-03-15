# Explore Verification Guide

This guide covers the verification process for explore workflows and what
to expect when comparing compiled output against Kibana exports.

## Verification process

### Prereq: Read compiler source

Read the relevant compiler source in `packages/kb-dashboard-core/src/` to
understand every supported config option and the view model defaults.

### Part 1: Compile YAML → Import → Verify in Kibana

For each supported feature:

1. **Author** a minimal YAML config exercising the feature.
2. **Compile** it: `just cli compile --input-file <file> --output-dir /tmp/compiled/`
3. **Import** the compiled NDJSON into Kibana:
   ```bash
   curl -X POST "http://localhost:5601/api/saved_objects/_import?overwrite=true" \
     -H "kbn-xsrf: true" --form file=@/tmp/compiled/<file>.ndjson
   ```
4. **Open** the imported panel in the Kibana editor and verify:
   - Every setting you specified in YAML is reflected in the UI
   - No settings are lost or silently dropped
   - The panel renders without errors
   - Kibana does not show warnings or "invalid" states
5. **Record** the result: feature name, YAML used, pass/fail, notes.

### Part 2: Create fresh panels in Kibana → Export → Compare to compiler

1. **Manually create** many fresh panels in Kibana from scratch, using a wide
   variety of settings. Cover edge cases, unusual combinations, and settings
   you haven't seen exercised in the YAML configs.
2. **Export** the dashboard:
   ```bash
   curl "http://localhost:5601/api/saved_objects/_export" \
     -H "kbn-xsrf: true" -H "Content-Type: application/json" \
     -d '{"type":"dashboard","includeReferencesDeep":true}'
   ```
3. **Inspect** the exported JSON and compare it against the compiler's view
   models and defaults. Look for:
   - Fields or settings Kibana produces that the compiler doesn't know about
   - Default values that differ from what the compiler sets
   - Structural patterns the compiler gets wrong
4. **Record** any discrepancies as potential compiler bugs or feature gaps.

## Fields to ignore in exported JSON

When comparing Kibana-exported JSON against the compiler's view models,
**ignore** the following fields. They are runtime artifacts or
non-deterministic values that will always differ and are **never** bugs:

- `adHocDataViews` / `indexPatternRefs` — Kibana runtime artifacts, not
  produced by the compiler
- `migrationVersion` / `typeMigrationVersion` / `coreMigrationVersion` —
  Kibana migration bookkeeping, varies by version
- Auto-generated `id` fields, `updatedAt`, `created_at`, `updated_at`,
  `version`, `namespaces`
- `references[].id` values — always unique per panel instance
- JSON key ordering differences — not meaningful
- `kibanaSavedObjectMeta.searchSourceJSON` differences in default empty
  filters/query — Kibana may add defaults the compiler omits

Only flag a difference as a bug if it affects a **functional setting** —
something that changes how the panel looks or behaves.

## Classifying findings

- **Bug**: The compiler produces incorrect JSON for a setting it claims to
  support — wrong field name, wrong value, wrong structure. The panel
  misbehaves or Kibana rejects it.
- **Gap**: Kibana supports a setting or field that the compiler has no config
  option for. Note it, but do NOT treat it as a bug.
- **Pass**: Compiled output works correctly in Kibana.

## Deliverable

**If no bugs are found**, do not create an issue. No-op.

**If bugs or significant findings exist**, create one GitHub issue.

**Issue title format:**
`[WORKFLOW_TAG-KIBANA_VERSION] N bugs, M gaps`

For example: `[explore-lens-xy-8.19.0] 3 bugs, 2 gaps`

If there are only bugs: `[explore-lens-xy-8.19.0] 3 bugs`
If there are only gaps: `[explore-lens-xy-8.19.0] 2 gaps`

**Issue body** — use **collapsed sections** (`<details>`) for:

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

Do not create branches or pull requests.

## Fix-and-verify workflow (when investigating known bugs)

When asked to validate or fix specific compiler bugs (e.g., from a triage
issue), follow this process for **each** bug:

1. **Reproduce** — Write a minimal YAML config that triggers the bug.
   Compile it with `just cli compile --input-file <file> --output-dir /tmp/compiled/`,
   import into Kibana, and confirm the bug exists.
2. **Show the diff** — Show the specific JSON fields the compiler produces
   vs what Kibana produces for the same panel. Create the panel manually in
   Kibana, export it, and compare the relevant fields only (ignore fields
   listed in "Fields to ignore" above).
3. **Fix it** — Find the exact file and line in
   `packages/kb-dashboard-core/src/` that causes the problem. Make the
   smallest possible change.
4. **Verify the fix** — Recompile the same YAML with your fix applied,
   reimport into Kibana, and confirm the panel now works correctly.
5. **Run tests** — Run `just core test` and `just core lint`. If tests
   fail because of your fix, update them to match the corrected behavior.
6. **Report** — For each bug, provide:
   - The YAML config that reproduces the bug
   - The compiler file and line you changed
   - What the change was (before → after)
   - Confirmation that Kibana accepts the fixed output
   - Any test changes made
