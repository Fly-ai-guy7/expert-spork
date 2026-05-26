#!/usr/bin/env bash
# Smoke-test the full pipeline by generating an IP case and running it.
set -euo pipefail

API="${API:-http://localhost:8000}"

echo "→ Generating an IP case..."
GEN=$(curl -s -X POST "$API/api/cases/generate" \
  -H 'Content-Type: application/json' \
  -d '{"area_of_law":"IP","difficulty":2,"language":"en"}')
CASE_ID=$(echo "$GEN" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")
echo "  case_id=$CASE_ID"

echo "→ Running simulation..."
curl -s -X POST "$API/api/cases/$CASE_ID/run" -H 'Content-Type: application/json' -d '{}' > /dev/null

echo "→ Waiting for completion..."
for i in {1..60}; do
  STATUS=$(curl -s "$API/api/cases/$CASE_ID/status" | python3 -c "import json,sys;print(json.load(sys.stdin)['status'])")
  echo "  [$i] status=$STATUS"
  if [[ "$STATUS" == "COMPLETE" || "$STATUS" == "FAILED" ]]; then
    break
  fi
  sleep 3
done

echo "→ Downloading PDF..."
curl -s "$API/api/cases/$CASE_ID/report.pdf" -o "case-$CASE_ID.pdf"
echo "  saved to case-$CASE_ID.pdf"
