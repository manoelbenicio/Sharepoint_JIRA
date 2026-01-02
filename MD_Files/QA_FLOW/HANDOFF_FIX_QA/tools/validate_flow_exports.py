#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Finding:
    zip_path: str
    definition_path: str
    json_path: str
    message: str


def _iter_json(node: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    yield path, node
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _iter_json(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _iter_json(v, f"{path}[{i}]")


def _is_probable_expression(s: str) -> bool:
    s2 = s.lstrip()
    if s2.startswith("@"):
        return True
    # If the string contains embedded expressions (e.g. JSON/templated text with "@{...}"),
    # it is valid for the outer string to be a literal and should not be treated as a single WDL expression.
    if "@{" in s2:
        return False
    # Heuristic: expression-like functions without '@' (common copy/paste/import failure)
    expr_markers = ("concat(", "coalesce(", "items(", "variables(", "outputs(", "triggerBody(", "utcNow(")
    return any(m in s2 for m in expr_markers)


def _wdl_balanced(expr: str) -> bool:
    in_quote = False
    balance = 0
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch == "'":
            if in_quote and i + 1 < len(expr) and expr[i + 1] == "'":
                i += 2
                continue
            in_quote = not in_quote
        if not in_quote:
            if ch == "(":
                balance += 1
            elif ch == ")":
                balance -= 1
                if balance < 0:
                    return False
        i += 1
    return balance == 0 and (not in_quote)


def _find_definition_json(zf: zipfile.ZipFile) -> str | None:
    candidates = [n for n in zf.namelist() if n.endswith("/definition.json")]
    if not candidates:
        return None
    # A flow export zip should have exactly one definition.json.
    return sorted(candidates)[0]


def validate_zip(zip_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        with zipfile.ZipFile(zip_path) as zf:
            definition_path = _find_definition_json(zf)
            if not definition_path:
                findings.append(
                    Finding(
                        zip_path=str(zip_path),
                        definition_path="(missing)",
                        json_path="$",
                        message="Missing definition.json (not a Power Automate flow export zip?)",
                    )
                )
                return findings

            try:
                definition = json.loads(zf.read(definition_path).decode("utf-8", errors="replace"))
            except Exception as e:  # noqa: BLE001
                findings.append(
                    Finding(
                        zip_path=str(zip_path),
                        definition_path=definition_path,
                        json_path="$",
                        message=f"definition.json is not valid JSON: {e}",
                    )
                )
                return findings

            for json_path, value in _iter_json(definition):
                if isinstance(value, list) and value and all(isinstance(v, str) for v in value):
                    # In Logic Apps, some fields are *expected* to be arrays of operands (e.g., Condition expression.equals),
                    # so we only flag arrays that strongly indicate a split expression or an invalid value type.
                    is_item_field = ".inputs.parameters.item/" in json_path
                    looks_split = len(value) >= 3 and any(_is_probable_expression(v) for v in value)
                    if is_item_field or looks_split:
                        findings.append(
                            Finding(
                                zip_path=str(zip_path),
                                definition_path=definition_path,
                                json_path=json_path,
                                message="Found list-of-strings where a single string expression/value is expected; import will fail (common cause: split @concat(...) fragments).",
                            )
                        )

                if isinstance(value, str) and _is_probable_expression(value):
                    # Expressions should be represented as a single string starting with '@'
                    if not value.lstrip().startswith("@"):
                        findings.append(
                            Finding(
                                zip_path=str(zip_path),
                                definition_path=definition_path,
                                json_path=json_path,
                                message="Expression-like string does not start with '@' (common copy/paste/import failure).",
                            )
                        )
                    if value.lstrip().startswith("@") and not _wdl_balanced(value):
                        findings.append(
                            Finding(
                                zip_path=str(zip_path),
                                definition_path=definition_path,
                                json_path=json_path,
                                message="Unbalanced parentheses/quotes in expression string (will fail import/runtime).",
                            )
                        )
    except zipfile.BadZipFile:
        findings.append(
            Finding(
                zip_path=str(zip_path),
                definition_path="(n/a)",
                json_path="$",
                message="Not a valid ZIP file.",
            )
        )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Power Automate flow export ZIPs for common import-breaking issues (split expressions, unbalanced WDL)."
    )
    parser.add_argument("--zips", nargs="+", required=True, help="One or more .zip files (or globs expanded by the shell).")
    args = parser.parse_args()

    zip_paths: list[Path] = []
    for p in args.zips:
        path = Path(p)
        if path.exists():
            zip_paths.append(path)
        else:
            # Keep going; report as a finding so CI/build fails deterministically.
            zip_paths.append(path)

    all_findings: list[Finding] = []
    for zp in zip_paths:
        if not zp.exists():
            all_findings.append(
                Finding(
                    zip_path=str(zp),
                    definition_path="(n/a)",
                    json_path="$",
                    message="ZIP path not found.",
                )
            )
            continue
        all_findings.extend(validate_zip(zp))

    if all_findings:
        for f in all_findings:
            print(f"ERROR: {f.zip_path} :: {f.definition_path} :: {f.json_path} :: {f.message}")
        return 2

    print(f"OK: validated {len(zip_paths)} zip(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
