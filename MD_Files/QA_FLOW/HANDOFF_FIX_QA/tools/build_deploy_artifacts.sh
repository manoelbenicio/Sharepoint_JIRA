#!/usr/bin/env bash
set -euo pipefail

ENV_PATH="${1:-.env}"
OUT_RENDERED="${2:-dist_rendered}"
OUT_ZIPS="${3:-dist_zips}"

python tools/sync_inputs_adaptive_card.py
python tools/patch_card_type_id.py --env "$ENV_PATH"
python tools/patch_flow1_weekly_card.py
python tools/patch_flow1_offer_query.py
python tools/patch_flow2_validation_gate.py
python tools/patch_flow2_rfp_link_gate.py
python tools/patch_flow2_offer_report_state.py
python tools/patch_flow3_consolidar_v2.py

python tools/render_flow_definitions.py --env "$ENV_PATH" --out "$OUT_RENDERED" --roots _prod_ac_patch
python tools/package_flow_exports.py --src-root "$OUT_RENDERED/_prod_ac_patch" --out "$OUT_ZIPS"

zips=(
  "$OUT_ZIPS/flow1.zip"
  "$OUT_ZIPS/flow2.zip"
  "$OUT_ZIPS/flow3.zip"
  "$OUT_ZIPS/flow4.zip"
)
for opt in "$OUT_ZIPS/flow1_queue_creator.zip" "$OUT_ZIPS/flow2_queue_wait.zip"; do
  if [[ -f "$opt" ]]; then
    zips+=("$opt")
  fi
done
python tools/validate_flow_exports.py --zips "${zips[@]}"

echo "DONE: artifacts ready in \`$OUT_ZIPS\`"
