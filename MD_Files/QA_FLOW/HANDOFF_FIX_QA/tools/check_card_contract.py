#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path


REQUIRED_SUBMIT_KEYS = {
    "action",
    "jirakey",
    "oferta_id",
    "semana",
    "arquiteto_email",
    "cardTypeId",
}


def find_definition_path(zf: zipfile.ZipFile) -> str | None:
    candidates = [n for n in zf.namelist() if n.endswith("/definition.json")]
    return sorted(candidates)[0] if candidates else None


def iter_cards(node):
    if isinstance(node, dict):
        # heuristic: adaptive card root
        if node.get("type") == "AdaptiveCard" and "body" in node:
            yield node
        for v in node.values():
            yield from iter_cards(v)
    elif isinstance(node, list):
        for v in node:
            yield from iter_cards(v)


def find_submit_actions(card: dict) -> list[dict]:
    actions = card.get("actions") or []
    return [a for a in actions if isinstance(a, dict) and a.get("type") == "Action.Submit"]


def validate_zip(zip_path: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    with zipfile.ZipFile(zip_path) as zf:
        defp = find_definition_path(zf)
        if not defp:
            return False, [f"{zip_path}: missing definition.json"]
        obj = json.loads(zf.read(defp))

    cards = list(iter_cards(obj))
    if not cards:
        errors.append(f"{zip_path}: no AdaptiveCard JSON found in definition")
        return False, errors

    ok_any = False
    for idx, card in enumerate(cards, start=1):
        submits = find_submit_actions(card)
        if not submits:
            continue
        for s in submits:
            data = s.get("data") or {}
            if not isinstance(data, dict):
                errors.append(f"{zip_path}: submit data is not an object (card #{idx})")
                continue
            missing = sorted(REQUIRED_SUBMIT_KEYS - set(data.keys()))
            if missing:
                errors.append(f"{zip_path}: missing submit keys {missing} (card #{idx})")
                continue
            ok_any = True

    if not ok_any and not errors:
        errors.append(f"{zip_path}: no Action.Submit found (or none with expected keys)")

    return ok_any and not errors, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Adaptive Card submit contract inside flow export zips.")
    parser.add_argument("--zips", nargs="+", required=True, help="Flow export zip paths (shell globs ok).")
    args = parser.parse_args()

    any_error = False
    for z in args.zips:
        ok, errs = validate_zip(Path(z))
        if ok:
            print(f"OK: {z}")
        else:
            any_error = True
            for e in errs:
                print(f"ERROR: {e}")
    return 2 if any_error else 0


if __name__ == "__main__":
    raise SystemExit(main())

