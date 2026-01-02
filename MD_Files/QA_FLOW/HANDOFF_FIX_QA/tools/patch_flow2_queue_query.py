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
    if len(candidates) > 1:
        # Power Automate exports usually contain exactly one flow definition.
        candidates = sorted(candidates)
    return candidates[0]


def patch_flow2_queue_query(zip_path: Path, *, recipient_email: str, top_count: int, order_by: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(td_path)
            definition_path = td_path / find_definition_path(zf)

        obj = json.loads(definition_path.read_text(encoding="utf-8", errors="replace"))
        actions = obj["properties"]["definition"]["actions"]
        if "Obter_itens_fila" not in actions:
            raise SystemExit("ERROR: expected action 'Obter_itens_fila' not found; update the patcher for this flow.")

        get_items = actions["Obter_itens_fila"]
        params = get_items.setdefault("inputs", {}).setdefault("parameters", {})

        # Safety filter: allow only a single recipient during tests.
        params["$filter"] = f"QueueStatus eq 'Pending' and RecipientEmail eq '{recipient_email}'"
        params["$top"] = int(top_count)
        params["$orderby"] = order_by

        definition_path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

        # Repack zip (preserve relative structure)
        tmp_zip = td_path / (zip_path.name + ".tmp")
        with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as out:
            for p in td_path.rglob("*"):
                if p.is_dir() or p == tmp_zip:
                    continue
                out.write(p, arcname=str(p.relative_to(td_path)))

        shutil.move(str(tmp_zip), str(zip_path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch Flow2 queue GetItems query in a flow export zip (flood-control safe defaults).")
    parser.add_argument("--zip", required=True, help="Path to flow2_queue_wait.zip")
    parser.add_argument("--recipient-email", default="mbenicios@minsait.com", help="Allowlist recipient email for safe runs")
    parser.add_argument("--top", type=int, default=1, help="Top Count for deterministic processing (default: 1)")
    parser.add_argument("--orderby", default="Created asc", help="Order By for deterministic processing (default: Created asc)")
    args = parser.parse_args()

    patch_flow2_queue_query(Path(args.zip), recipient_email=args.recipient_email, top_count=args.top, order_by=args.orderby)
    print(f"OK: patched {args.zip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

