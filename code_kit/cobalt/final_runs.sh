#!/usr/bin/env bash
# Five hand-in runs in parallel, then package + check.py. Same command for the mock dress rehearsal and the live runs.
#   bash code_kit/cobalt/final_runs.sh mock     # free, ~10 s
#   bash code_kit/cobalt/final_runs.sh live     # gemini-3.7-flash, ~5-10 min
set -euo pipefail
MODE=${1:-mock}
cd "$(dirname "$0")/../.."
PY=.venv/bin/python
LIVE=""; LABEL="final-dry"
if [ "$MODE" = "live" ]; then LIVE="--live"; LABEL="final"; fi
COMMON=(--decisions final --model final --label "$LABEL" $LIVE
        --set 'run.team="team-04"' --set llm.timeout_s=10 --set llm.concurrency=100)
LOG=code_kit/cobalt/outputs/final_logs/$(date +%Y%m%d-%H%M%S)_$MODE
mkdir -p "$LOG"

$PY -m code_kit.cobalt.run --type plan             --seed 1 "${COMMON[@]}"            > "$LOG/plan_1.log" 2>&1 &
$PY -m code_kit.cobalt.run --type plan             --seed 2 "${COMMON[@]}" --no-probe > "$LOG/plan_2.log" 2>&1 &
$PY -m code_kit.cobalt.run --type nodecision       --seed 1 "${COMMON[@]}"            > "$LOG/nodecision_1.log" 2>&1 &
$PY -m code_kit.cobalt.run --type nodecision       --seed 2 "${COMMON[@]}" --no-probe > "$LOG/nodecision_2.log" 2>&1 &
$PY -m code_kit.cobalt.run --type plan_nosurprises --seed 1 "${COMMON[@]}" --no-probe > "$LOG/plan_nosurprises.log" 2>&1 &
wait

ARGS=()
for slot in plan_1 plan_2 nodecision_1 nodecision_2 plan_nosurprises; do
  dir=$(tail -n 1 "$LOG/$slot.log")
  if [ ! -d "$dir" ]; then echo "FAILED: $slot (see $LOG/$slot.log)"; exit 1; fi
  grep "done in\|SANITY" "$LOG/$slot.log" || true
  ARGS+=("--$slot" "$dir")
done
$PY -m code_kit.cobalt.package "${ARGS[@]}" --set 'run.team="team-04"' | tee "$LOG/package.log"
