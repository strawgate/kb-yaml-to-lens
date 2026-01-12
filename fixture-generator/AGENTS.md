# Agent Guidelines: Fixture Generator

> Docker-based TypeScript fixture generator using Kibana's LensConfigBuilder API

---

## Quick Start

See README.md for setup and FIXTURES.md for development guidelines.

---

## Critical Rules

**When creating/modifying fixtures:**

1. Run `cd fixture-generator && make pull` (first time only)
2. Run `cd fixture-generator && make run-example EXAMPLE=<your-file>.ts`
3. Verify output in `fixture-generator/output/`
4. Commit BOTH script AND output files

**Why:** Ensures compiler produces JSON that works in Kibana. Provides accurate reference.

**No Docker?** State clearly and request user verification before merging.
