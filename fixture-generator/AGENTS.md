# Agent Guidelines: Fixture Generator

> Docker-based TypeScript fixture generator using Kibana's LensConfigBuilder API

---

## Quick Start

@README.md

---

## Development Guidelines

@FIXTURES.md

---

## Critical Agent Rules

### Fixture Generation is Required

We're building a compiler targeting Kibana's JSON format. The fixture generator produces valid Kibana JSON using official APIs—much faster than manual creation.

**When creating/modifying fixtures:**

1. Run `cd fixture-generator && make pull` (first time only - pulls pre-built base image)
2. Run `cd fixture-generator && make run-example EXAMPLE=<your-file>.ts`
3. Verify output exists in `fixture-generator/output/`
4. Inspect JSON validity
5. Commit BOTH script AND output files

**Why:** Ensures compiler produces JSON that works in Kibana. Provides accurate reference. Catches schema changes.

**If you can't run Docker:** State this clearly and request user verification before merging.

---

## Summary Checklist

**Before commit:** `make typecheck` → `make run-example EXAMPLE=your-file.ts` → verify output exists → validate JSON (`python -m json.tool`) → `make ci` from root → commit

**No Docker?** State clearly, request user testing.
