# Agent Guidelines: Dashboard Core (Python)

> Pure compilation engine for YAML to Kibana dashboard format

## Introduction

@README.md

---

## Development Guide

See [DEVELOPING.md](../../DEVELOPING.md) for development setup and workflows.

---

## Code Style

@CODE_STYLE.md

---

## Package Scope

This package is intentionally minimal and focused:

- **Pure compilation** — YAML config models to Kibana JSON view models
- **No external dependencies** — No HTTP clients, no CLI frameworks, no LSP
- **Strict separation** — Config models (input), view models (output), compile functions (transformation)

If you need HTTP clients, CLI tooling, or LSP features, use `kb-dashboard-cli` or `kb-dashboard-tools` instead.
