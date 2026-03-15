# Explore Agent: Verification Process

## Prereq: Read compiler source

Read the relevant compiler source in `packages/kb-dashboard-core/src/` to
understand every supported config option and the view model defaults.

## Part 1: Compile YAML → Import → Verify in Kibana

For each supported feature:

1. **Author** a minimal YAML config exercising the feature.
2. **Compile and upload** in one step:
   ```bash
   uv run kb-dashboard compile --input-file <file> --output-dir /tmp/compiled/ \
     --upload --kibana-url http://host.docker.internal:5601
   ```
   This compiles the YAML to NDJSON and uploads it to Kibana via the
   saved objects API. Do NOT use curl or the Kibana UI to import — the
   CLI handles it reliably.
3. **Open** the imported panel in the Kibana editor and verify:
   - Every setting you specified in YAML is reflected in the UI
   - No settings are lost or silently dropped
   - The panel renders without errors
   - Kibana does not show warnings or "invalid" states
4. **Record** the result: feature name, YAML used, pass/fail, notes.

## Part 2: Create fresh panels in Kibana → Export → Compare to compiler

1. **Manually create** many fresh panels in Kibana from scratch, using a wide
   variety of settings. Cover edge cases, unusual combinations, and settings
   you haven't seen exercised in the YAML configs.
2. **Export** the dashboard using the CLI:
   ```bash
   uv run kb-dashboard fetch <dashboard-id> --output /tmp/exported.ndjson \
     --kibana-url http://host.docker.internal:5601
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

## Fix-and-verify workflow (when investigating known bugs)

When asked to validate or fix specific compiler bugs (e.g., from a triage
issue), follow this process for **each** bug:

1. **Reproduce** — Write a minimal YAML config that triggers the bug.
   Compile and upload it:
   ```bash
   uv run kb-dashboard compile --input-file <file> --output-dir /tmp/compiled/ \
     --upload --kibana-url http://host.docker.internal:5601
   ```
   Open the dashboard in Kibana and confirm the bug exists.
2. **Show the diff** — Show the specific JSON fields the compiler produces
   vs what Kibana produces for the same panel. Create the panel manually in
   Kibana, export it, and compare the relevant fields only (ignore fields
   listed in "Fields to ignore" above).
3. **Fix it** — Find the exact file and line in
   `packages/kb-dashboard-core/src/` that causes the problem. Make the
   smallest possible change.
4. **Verify the fix** — Recompile and re-upload with your fix applied:
   ```bash
   uv run kb-dashboard compile --input-file <file> --output-dir /tmp/compiled/ \
     --upload --kibana-url http://host.docker.internal:5601
   ```
   Open in Kibana and confirm the panel now works correctly.
5. **Run tests** — Run `just core test` and `just core lint`. If tests
   fail because of your fix, update them to match the corrected behavior.
6. **Report** — For each bug, provide:
   - The YAML config that reproduces the bug
   - What you observed in the Kibana UI (before and after the fix)
   - The compiler file and line you changed
   - What the change was (before → after)
   - Confirmation that Kibana accepts the fixed output
   - Any test changes made

**Do not skip the Kibana steps.** A fix that was only verified by reading
code is not a verified fix. You have a live Kibana instance — use it.
