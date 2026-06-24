#!/usr/bin/env bash
#
# Smoke-test the Luxor Guest House API against a running backend.
#
# Usage:
#   API=https://luxor-guest-house-api.onrender.com ./scripts/smoke_api.sh
#   ./scripts/smoke_api.sh http://localhost:8000
#
# No external tools required (no jq). Uses curl + grep only.
# Exits non-zero on the first failed check.
set -euo pipefail

API="${1:-${API:-http://localhost:8000}}"
API="${API%/}"   # strip a trailing slash
fail=0

echo "Smoke-testing Luxor Guest House API at: $API"
echo

# check <label> <method> <path> [must-contain] [json-body]
check() {
  local label="$1" method="$2" path="$3" needle="${4:-}" body="${5:-}"
  local url="$API$path"
  local out http

  if [ "$method" = "POST" ]; then
    out=$(curl -sS -m 30 -w $'\n%{http_code}' -X POST "$url" \
      -H "Content-Type: application/json" -d "$body") || { echo "FAIL  $label  (curl error)"; fail=1; return; }
  else
    out=$(curl -sS -m 30 -w $'\n%{http_code}' "$url") || { echo "FAIL  $label  (curl error)"; fail=1; return; }
  fi

  http="${out##*$'\n'}"
  out="${out%$'\n'*}"

  if [ "$http" -lt 200 ] || [ "$http" -ge 300 ]; then
    echo "FAIL  $label  (HTTP $http)"
    fail=1
    return
  fi
  if [ -n "$needle" ] && ! printf '%s' "$out" | grep -q "$needle"; then
    echo "FAIL  $label  (HTTP $http, missing '$needle')"
    fail=1
    return
  fi
  echo "PASS  $label  (HTTP $http)"
}

check "root"               GET  "/"               '"status"'
check "rooms"              GET  "/api/rooms"      '"name"'
check "tours"              GET  "/api/tours"      '"name"'
check "dashboard"          GET  "/api/dashboard"  '"kpis"'
check "concierge"          POST "/api/concierge"  '"reply"'   '{"message":"Which rooms have a river view?"}'
check "booking (create)"   POST "/api/bookings"   '"ok"'      '{"name":"Smoke Test","email":"smoke@example.com","guests":2}'

echo
if [ "$fail" -ne 0 ]; then
  echo "Smoke test FAILED."
  exit 1
fi
echo "Smoke test passed."
