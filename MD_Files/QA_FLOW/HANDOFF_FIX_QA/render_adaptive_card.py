#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"\$\{([^}]+)\}")


def _render_value(value, data, used_keys, missing_keys):
    if isinstance(value, dict):
        return {k: _render_value(v, data, used_keys, missing_keys) for k, v in value.items()}
    if isinstance(value, list):
        return [_render_value(v, data, used_keys, missing_keys) for v in value]
    if isinstance(value, str):
        def repl(match):
            key = match.group(1).strip()
            used_keys.add(key)
            if key not in data:
                missing_keys.add(key)
                return ""
            replacement = data[key]
            return "" if replacement is None else str(replacement)

        return PLACEHOLDER_RE.sub(repl, value)
    return value


def main():
    parser = argparse.ArgumentParser(description="Renderiza um template de Adaptive Card (${chaves}) com um JSON de dados.")
    parser.add_argument("--template", default="adaptive_card.json", help="Caminho do template do card (default: adaptive_card.json)")
    parser.add_argument("--data", default="adaptive_card.data.json", help="Caminho do JSON de dados (default: adaptive_card.data.json)")
    parser.add_argument("--out", default="adaptive_card.rendered.json", help="Arquivo de saída do card renderizado")
    parser.add_argument(
        "--teams-payload-out",
        default="teams.webhook.payload.json",
        help="Arquivo de saída com wrapper para Incoming Webhook do Teams",
    )
    parser.add_argument("--no-teams-payload", action="store_true", help="Não gerar o wrapper de payload do Teams")
    parser.add_argument("--non-strict", action="store_true", help="Não falhar se faltar alguma chave (substitui por vazio)")

    args = parser.parse_args()

    template_path = Path(args.template)
    data_path = Path(args.data)

    template = json.loads(template_path.read_text(encoding="utf-8"))
    data = json.loads(data_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("--data precisa ser um objeto JSON (dicionário).")

    used_keys = set()
    missing_keys = set()
    rendered = _render_value(template, data, used_keys, missing_keys)

    if missing_keys and not args.non_strict:
        missing_list = ", ".join(sorted(missing_keys))
        raise SystemExit(f"Faltam chaves no JSON de dados: {missing_list}")

    Path(args.out).write_text(json.dumps(rendered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not args.no_teams_payload:
        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": rendered,
                }
            ],
        }
        Path(args.teams_payload_out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    used_list = ", ".join(sorted(used_keys)) if used_keys else "-"
    print(f"OK: gerado `{args.out}` (keys usadas: {used_list})")
    if not args.no_teams_payload:
        print(f"OK: gerado `{args.teams_payload_out}`")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
