#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/run_analysis_and_llm.sh /full/path/to/video.mp4

VIDEO="$1"
ANALYZE_OUT="analyze_response.json"
BITNET_OUT="bitnet_response.json"
HOST="http://127.0.0.1:8000"

echo "Uploading ${VIDEO} to ${HOST}/analyze..."
curl -sS -X POST "${HOST}/analyze" -F "file=@${VIDEO}" -o "${ANALYZE_OUT}"

echo "Saved analysis to ${ANALYZE_OUT}."
echo "Attempting to extract a candidate utterance and emotions from timeline..."

utterance=$(jq -r '(.timeline[]? | .text // .utterance // .transcript) | select(.!=null)' "${ANALYZE_OUT}" | head -n1 || true)
from=$(jq -r '(.timeline[]? | .from_emotion // .prev_emotion // .start_emotion) | select(.!=null)' "${ANALYZE_OUT}" | head -n1 || true)
to=$(jq -r '(.timeline[]? | .to_emotion // .emotion // .end_emotion // .detected_emotion) | select(.!=null)' "${ANALYZE_OUT}" | head -n1 || true)

if [ -z "${utterance}" ]; then
  echo "No utterance found automatically in timeline."
  read -p "Enter text to analyze (press Enter when done): " utterance
fi

echo "Utterance: ${utterance}"
echo "From emotion: ${from:-<empty>}"
echo "To emotion: ${to:-<empty>}"

payload=$(jq -n --arg t "${utterance}" --arg f "${from}" --arg tt "${to}" \
  '{text:$t} + (if $f!="" then {from_emotion:$f} else {} end) + (if $tt!="" then {to_emotion:$tt} else {} end)')

echo "Calling ${HOST}/bitnet/analyze..."
curl -sS -X POST "${HOST}/bitnet/analyze" -H "Content-Type: application/json" -d "${payload}" -o "${BITNET_OUT}"

echo "LLM response saved to ${BITNET_OUT}"
jq . "${BITNET_OUT}"

echo "Done."
