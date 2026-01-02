#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import zipfile
from copy import deepcopy
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

        root_actions = obj["properties"]["definition"]["actions"]
        loop = root_actions["Aplicar_a_cada_fila"]["actions"]
        ifnode = loop["Verificar_QueueStatus_Pending"]
        actions = ifnode["actions"]

        if "Atualizar_Queue_para_Sent" not in actions:
            raise SystemExit("ERROR: expected action 'Atualizar_Queue_para_Sent' not found; update patcher.")

        # Insert a Processing step before the legacy "Atualizar_Queue_para_Sent".
        # This avoids marking items as Sent too early and provides a lock + attempt counter.
        update_sent = actions["Atualizar_Queue_para_Sent"]
        sent_params = update_sent["inputs"]["parameters"]
        dataset = sent_params["dataset"]
        table = sent_params["table"]
        item_id = sent_params["id"]

        update_processing = deepcopy(update_sent)
        update_processing["runAfter"] = {}
        update_processing["inputs"]["parameters"] = {
            "dataset": dataset,
            "table": table,
            "id": item_id,
            "item/QueueStatus/Value": "Processing",
            "item/AttemptCount": "@add(int(coalesce(items('Aplicar_a_cada_fila')?['AttemptCount'], 0)), 1)",
        }

        # Rewire legacy action to truly mean "Sent" (right before the Teams post/wait).
        update_sent["runAfter"] = {"Atualizar_Queue_para_Processing": ["Succeeded"]}
        update_sent["inputs"]["parameters"] = {
            "dataset": dataset,
            "table": table,
            "id": item_id,
            "item/QueueStatus/Value": "Sent",
            "item/SentAt": "@utcNow()",
        }

        # Insert Processing action into the actions dict preserving relative ordering as best as possible.
        # Place it before the legacy Sent action.
        new_actions = {}
        for k, v in actions.items():
            if k == "Atualizar_Queue_para_Sent":
                new_actions["Atualizar_Queue_para_Processing"] = update_processing
            new_actions[k] = v
        actions.clear()
        actions.update(new_actions)

        # Teams failure handler: if PostCardAndWait fails, mark queue item as Error.
        post_action_name = "Postar_cartao_e_aguardar_resposta"
        if post_action_name not in actions:
            raise SystemExit(f"ERROR: expected action '{post_action_name}' not found; update patcher.")

        error_on_teams = deepcopy(update_sent)
        error_on_teams["runAfter"] = {post_action_name: ["Failed", "TimedOut"]}
        error_on_teams["inputs"]["parameters"] = {
            "dataset": dataset,
            "table": table,
            "id": item_id,
            "item/QueueStatus/Value": "Error",
        }
        error_on_teams["inputs"]["parameters"]["item/QueueStatus/Value"] = "Error"
        # Do not stamp CompletedAt here; only Completed path stamps it.

        # Insert action (name must be unique)
        if "Atualizar_Queue_para_Error_Teams" not in actions:
            actions["Atualizar_Queue_para_Error_Teams"] = error_on_teams

        # Completed stamp (after persistence)
        vd = actions["Validar_observacoes_vermelho"]
        dup_else = vd["else"]["actions"]["Verificar_duplicidade"]["else"]["actions"]
        if "Atualizar_Queue_para_Completed" not in dup_else:
            raise SystemExit("ERROR: expected action 'Atualizar_Queue_para_Completed' not found; update patcher.")

        completed = dup_else["Atualizar_Queue_para_Completed"]
        comp_params = completed["inputs"]["parameters"]
        comp_params["item/QueueStatus/Value"] = "Completed"
        comp_params["item/CompletedAt"] = "@utcNow()"

        # Persistence failure handler: if history create fails, mark queue item as Error.
        create_hist = "Criar_item_StatusReports_Historico"
        if create_hist not in dup_else:
            raise SystemExit(f"ERROR: expected action '{create_hist}' not found; update patcher.")

        error_on_persist = deepcopy(update_sent)
        error_on_persist["runAfter"] = {create_hist: ["Failed", "TimedOut"]}
        error_on_persist["inputs"]["parameters"] = {
            "dataset": dataset,
            "table": table,
            "id": item_id,
            "item/QueueStatus/Value": "Error",
        }

        if "Atualizar_Queue_para_Error_Persistencia" not in dup_else:
            dup_else["Atualizar_Queue_para_Error_Persistencia"] = error_on_persist

        definition_path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

        tmp_zip = td_path / (zip_path.name + ".tmp")
        with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as out:
            for p in td_path.rglob("*"):
                if p.is_dir() or p == tmp_zip:
                    continue
                out.write(p, arcname=str(p.relative_to(td_path)))

        shutil.move(str(tmp_zip), str(zip_path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch Flow2 export zip to use a safer queue state machine + stamps.")
    parser.add_argument("--zip", required=True, help="Path to flow2_queue_wait.zip")
    args = parser.parse_args()
    patch(Path(args.zip))
    print(f"OK: patched {args.zip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
