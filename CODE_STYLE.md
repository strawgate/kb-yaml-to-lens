# Code Style Guide

This document describes code style conventions that are **atypical** but **mandatory** in this project. These conventions apply project-wide; see component-specific CODE_STYLE.md files for language-specific details.

## General Principles

### Explicit Over Implicit

This project favors explicitness over brevity. Code should be immediately readable without requiring deep context.

### Pattern Consistency

When making changes, search the codebase for similar patterns first. If a pattern exists across multiple files, it's likely intentional—follow it unless you have strong justification to diverge.

### Documentation

- Document **why**, not **what**
- Avoid obvious comments that restate the code
- Use docstrings for public APIs

## Component-Specific Styles

Each component has its own CODE_STYLE.md with language-specific conventions:

- **Python (compiler):** [compiler/CODE_STYLE.md](compiler/CODE_STYLE.md)
- **TypeScript (vscode-extension):** [vscode-extension/CODE_STYLE.md](vscode-extension/CODE_STYLE.md)
