#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import zipfile
from pathlib import Path


def find_definition_path(zf: zipfile.ZipFile) -> str:
    candidates = [n for n in zf.namelist() if n.endswith("/definition.json")]
    if not candidates:
        raise SystemExit("ERROR: no definition.json found in zip (not a flow export?)")
    return sorted(candidates)[0]


def patch_flow4(zip_path: Path, *, action_name: str, placeholder_uri: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(td_path)
            definition_path = td_path / find_definition_path(zf)

        obj = json.loads(definition_path.read_text(encoding="utf-8", errors="replace"))
        actions = obj["properties"]["definition"]["actions"]

        if action_name not in actions:
            raise SystemExit(f"ERROR: action '{action_name}' not found in Flow4 export; update patcher.")

        http_action = actions[action_name]
        if http_action.get("type") != "Http":
            raise SystemExit(f"ERROR: action '{action_name}' is not type Http; update patcher.")

        http_action.setdefault("inputs", {})["uri"] = placeholder_uri

        definition_path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

        tmp_zip = td_path / (zip_path.name + ".tmp")
        with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as out:
            for p in td_path.rglob("*"):
                if p.is_dir() or p == tmp_zip:
                    continue
                out.write(p, arcname=str(p.relative_to(td_path)))

        shutil.move(str(tmp_zip), str(zip_path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch Flow4 export zip to remove secrets from HTTP action URI (placeholder).")
    parser.add_argument("--zip", required=True, help="Path to flow4.zip")
    parser.add_argument("--action-name", default="HTTP", help="HTTP action name (default: HTTP)")
    parser.add_argument(
        "--uri",
        default="https://func-pipeline-consolidation.azurewebsites.net/api/import-jira?code=<FUNCTION_KEY>",
        help="Placeholder URI to write into the flow export",
    )
    args = parser.parse_args()
    patch_flow4(Path(args.zip), action_name=args.action_name, placeholder_uri=args.uri)
    print(f"OK: patched {args.zip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

