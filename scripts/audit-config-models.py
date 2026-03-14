#!/usr/bin/env python3
"""Audit Pydantic config models for configuration drift across packages.

Scans all Python files for Pydantic model_config definitions and reports
inconsistencies: redundant redefinitions, missing settings, mismatched
values, and non-standard patterns.

Exit codes:
    0 — no drift detected
    1 — drift detected (findings printed to stdout as Markdown)
"""

from __future__ import annotations

import ast
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Canonical settings from kb_dashboard_core.shared.model.BaseModel
CANONICAL_SETTINGS: dict[str, object] = {
    'strict': True,
    'validate_default': True,
    'extra': 'forbid',
    'use_enum_values': True,
    'frozen': True,
    'use_attribute_docstrings': True,
    'serialize_by_alias': True,
}

# Root‑model canonical settings (no extra)
CANONICAL_ROOT_SETTINGS: dict[str, object] = {
    k: v for k, v in CANONICAL_SETTINGS.items() if k != 'extra'
}

# Classes whose model_config defines the canonical settings — skip them.
CANONICAL_DEFINING_CLASSES = frozenset({'BaseModel', 'BaseRootCfgModel'})

# Base classes that carry the canonical config (no need to redefine).
INHERITS_CANONICAL = frozenset({
    'BaseModel',
    'BaseCfgModel',
    'BaseIdentifiableModel',
    'BasePanel',
    'BaseRootCfgModel',
})

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class ModelConfigInfo:
    """Parsed model_config for a single class."""

    file: Path
    line: int
    class_name: str
    bases: list[str]
    settings: dict[str, object]
    style: str  # 'ConfigDict' | 'dict_literal'


@dataclass
class Finding:
    """A single audit finding."""

    file: Path
    line: int
    class_name: str
    category: str
    message: str


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _eval_constant(node: ast.expr) -> object:
    """Attempt to evaluate a simple constant AST node."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant):
        return -node.operand.value  # type: ignore[operator]
    return None


def _parse_configdict_call(node: ast.Call) -> dict[str, object] | None:
    """Extract keyword arguments from a ConfigDict(...) call."""
    result: dict[str, object] = {}
    for kw in node.keywords:
        if kw.arg is None:
            continue
        val = _eval_constant(kw.value)
        if val is not None:
            result[kw.arg] = val
    return result


def _parse_dict_literal(node: ast.Dict) -> dict[str, object] | None:
    """Extract entries from a dict literal like {'extra': 'forbid', ...}."""
    result: dict[str, object] = {}
    for key, value in zip(node.keys, node.values):
        if key is None or value is None:
            continue
        k = _eval_constant(key)
        v = _eval_constant(value)
        if isinstance(k, str) and v is not None:
            result[k] = v
    return result


def _get_base_names(node: ast.ClassDef) -> list[str]:
    """Return simple base‑class names for a class definition."""
    names: list[str] = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
        elif isinstance(base, ast.Subscript) and isinstance(base.value, ast.Name):
            names.append(base.value.id)
    return names


# ---------------------------------------------------------------------------
# File scanning
# ---------------------------------------------------------------------------

def _scan_file(path: Path) -> list[ModelConfigInfo]:
    """Parse a Python file and return model_config info for every class."""
    try:
        source = path.read_text(encoding='utf-8')
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return []

    results: list[ModelConfigInfo] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        bases = _get_base_names(node)

        for item in node.body:
            if not isinstance(item, (ast.Assign, ast.AnnAssign)):
                continue

            # Determine target name
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                target_name = item.target.id
            elif isinstance(item, ast.Assign) and len(item.targets) == 1 and isinstance(item.targets[0], ast.Name):
                target_name = item.targets[0].id
            else:
                continue

            if target_name != 'model_config':
                continue

            value = item.value
            if value is None:
                continue

            settings: dict[str, object] | None = None
            style = 'unknown'

            if isinstance(value, ast.Call):
                func = value.func
                is_configdict = (
                    (isinstance(func, ast.Name) and func.id == 'ConfigDict')
                    or (isinstance(func, ast.Attribute) and func.attr == 'ConfigDict')
                )
                if is_configdict:
                    settings = _parse_configdict_call(value)
                    style = 'ConfigDict'
            elif isinstance(value, ast.Dict):
                settings = _parse_dict_literal(value)
                style = 'dict_literal'

            if settings is not None:
                results.append(ModelConfigInfo(
                    file=path,
                    line=item.lineno,
                    class_name=node.name,
                    bases=bases,
                    settings=settings,
                    style=style,
                ))
    return results


def _discover_python_files(root: Path) -> list[Path]:
    """Find all Python files under root, excluding venvs and caches."""
    excluded = {'.venv', '__pycache__', 'node_modules', '.git'}
    results: list[Path] = []
    for p in root.rglob('*.py'):
        if any(part in excluded for part in p.parts):
            continue
        results.append(p)
    return sorted(results)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def _inherits_canonical(info: ModelConfigInfo) -> bool:
    return bool(set(info.bases) & INHERITS_CANONICAL)


def _analyze(infos: list[ModelConfigInfo]) -> list[Finding]:
    """Produce findings from collected model config info."""
    findings: list[Finding] = []

    # Group by (settings‑dict, style) to detect clusters
    pattern_groups: dict[str, list[ModelConfigInfo]] = defaultdict(list)

    for info in infos:
        # Skip canonical defining classes
        if info.class_name in CANONICAL_DEFINING_CLASSES:
            continue

        rel = info.file.relative_to(REPO_ROOT)

        # ---- Check: dict literal instead of ConfigDict -------------------
        if info.style == 'dict_literal':
            findings.append(Finding(
                file=info.file,
                line=info.line,
                class_name=info.class_name,
                category='non-standard-style',
                message=(
                    f'`{info.class_name}` uses a plain `dict` for '
                    f'`model_config` instead of `ConfigDict(...)` '
                    f'({rel}:{info.line})'
                ),
            ))

        # ---- Check: redundant redefinition when inheriting canonical -----
        if _inherits_canonical(info):
            # If settings are a pure subset of (or equal to) canonical
            # the redefinition may be intentional (e.g. overriding extra).
            # Flag if settings exactly match canonical — truly redundant.
            if info.settings == CANONICAL_SETTINGS:
                findings.append(Finding(
                    file=info.file,
                    line=info.line,
                    class_name=info.class_name,
                    category='redundant-redefinition',
                    message=(
                        f'`{info.class_name}` redefines `model_config` '
                        f'with identical canonical settings — '
                        f'remove the redefinition '
                        f'({rel}:{info.line})'
                    ),
                ))

        # ---- Check: missing canonical settings ---------------------------
        # Only flag classes that define their own full model_config
        # (not intentional single-override like extra='allow').
        if len(info.settings) >= 3:  # noqa: PLR2004
            missing = {
                k: v
                for k, v in CANONICAL_SETTINGS.items()
                if k not in info.settings
            }
            if missing:
                missing_keys = ', '.join(f'`{k}`' for k in sorted(missing))
                findings.append(Finding(
                    file=info.file,
                    line=info.line,
                    class_name=info.class_name,
                    category='missing-settings',
                    message=(
                        f'`{info.class_name}` defines `model_config` with '
                        f'{len(info.settings)} settings but is missing '
                        f'{missing_keys} compared to the canonical config '
                        f'({rel}:{info.line})'
                    ),
                ))

        # ---- Check: value mismatch against canonical --------------------
        for k, v in info.settings.items():
            if k in CANONICAL_SETTINGS and CANONICAL_SETTINGS[k] != v:
                # Intentional overrides (like extra='allow') are expected
                # in some cases — still worth surfacing for review.
                findings.append(Finding(
                    file=info.file,
                    line=info.line,
                    class_name=info.class_name,
                    category='value-mismatch',
                    message=(
                        f'`{info.class_name}` sets `{k}={v!r}` but '
                        f'canonical is `{k}={CANONICAL_SETTINGS[k]!r}` '
                        f'({rel}:{info.line})'
                    ),
                ))

        # Track patterns for cluster analysis
        key = str(sorted(info.settings.items()))
        pattern_groups[key].append(info)

    return findings


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _format_markdown(findings: list[Finding]) -> str:
    """Format findings as a Markdown report."""
    by_category: dict[str, list[Finding]] = defaultdict(list)
    for f in findings:
        by_category[f.category].append(f)

    category_titles: dict[str, str] = {
        'non-standard-style': 'Non-Standard Style (dict literal instead of ConfigDict)',
        'redundant-redefinition': 'Redundant Redefinition (identical to inherited canonical)',
        'missing-settings': 'Missing Canonical Settings',
        'value-mismatch': 'Value Mismatch Against Canonical Config',
    }

    lines: list[str] = []
    lines.append('## Configuration Model Audit Results\n')
    lines.append(f'Found **{len(findings)}** finding(s) across '
                 f'**{len(by_category)}** category/categories.\n')

    lines.append('### Canonical Settings Reference\n')
    lines.append('Defined in `packages/kb-dashboard-core/src/kb_dashboard_core/shared/model.py`:\n')
    lines.append('```python')
    for k, v in CANONICAL_SETTINGS.items():
        lines.append(f'  {k}={v!r},')
    lines.append('```\n')

    for cat in ['non-standard-style', 'redundant-redefinition', 'missing-settings', 'value-mismatch']:
        items = by_category.get(cat)
        if not items:
            continue

        title = category_titles.get(cat, cat)
        lines.append(f'### {title}\n')
        for item in sorted(items, key=lambda f: (str(f.file), f.line)):
            lines.append(f'- {item.message}')
        lines.append('')

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    """Run the config model audit and print results."""
    python_files = _discover_python_files(REPO_ROOT / 'packages')
    all_infos: list[ModelConfigInfo] = []
    for pf in python_files:
        all_infos.extend(_scan_file(pf))

    findings = _analyze(all_infos)

    if not findings:
        print('No configuration drift detected.')
        return 0

    report = _format_markdown(findings)
    print(report)
    return 1


if __name__ == '__main__':
    sys.exit(main())
