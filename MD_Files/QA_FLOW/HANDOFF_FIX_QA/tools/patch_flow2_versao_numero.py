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


def patch(zip_path: Path) -> None:
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(td_path)
            definition_path = td_path / find_definition_path(zf)

        obj = json.loads(definition_path.read_text(encoding="utf-8", errors="replace"))

        actions = obj["properties"]["definition"]["actions"]
        create_hist = (
            actions["Aplicar_a_cada_fila"]["actions"]["Verificar_QueueStatus_Pending"]["actions"]["Validar_observacoes_vermelho"][
                "else"
            ]["actions"]["Verificar_duplicidade"]["else"]["actions"]["Criar_item_StatusReports_Historico"]
        )

        params = create_hist["inputs"]["parameters"]
        # Use card payload versao_report if available; fallback to queue VersaoReport; default 1.
        params["item/VersaoNumero"] = (
            "@int(coalesce(outputs('Compor_ResponseData')?['versao_report'], items('Aplicar_a_cada_fila')?['VersaoReport'], 1))"
        )

        definition_path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

        tmp_zip = td_path / (zip_path.name + ".tmp")
        with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as out:
            for p in td_path.rglob("*"):
                if p.is_dir() or p == tmp_zip:
                    continue
                out.write(p, arcname=str(p.relative_to(td_path)))

        shutil.move(str(tmp_zip), str(zip_path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch Flow2 export zip to persist VersaoNumero dynamically from card payload.")
    parser.add_argument("--zip", required=True, help="Path to flow2_queue_wait.zip")
    args = parser.parse_args()
    patch(Path(args.zip))
    print(f"OK: patched {args.zip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

