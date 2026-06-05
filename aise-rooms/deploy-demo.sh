#!/usr/bin/env bash
# Deploy (or locally preview) a white-label AISE Rooms demo instance.
#
# Each demo = the SHARED index.html + the demo's own brand.js. This script
# assembles them into a temp build dir so there are no Docker build-context
# gymnastics, then runs `fly deploy` (or a local nginx preview with --preview).
#
# Usage:
#   ./deploy-demo.sh <demo-name>            # fly deploy
#   ./deploy-demo.sh <demo-name> --preview  # build + run locally on :8080
#
# Available demos: any directory under ./demos/ containing brand.js + fly.toml.

set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
demo="${1:-}"
mode="${2:-deploy}"

if [[ -z "$demo" || ! -d "$root/demos/$demo" ]]; then
  echo "Usage: $0 <demo-name> [--preview]"
  echo "Demos:"; ls -1 "$root/demos" 2>/dev/null | sed 's/^/  - /'
  exit 1
fi

src="$root/demos/$demo"
build="$(mktemp -d)"
trap 'rm -rf "$build"' EXIT

cp "$root/index.html" "$build/index.html"
cp "$root/Dockerfile" "$build/Dockerfile"
cp "$src/brand.js"    "$build/brand.js"
cp "$src/fly.toml"    "$build/fly.toml"
echo "Assembled '$demo' build in $build"

if [[ "$mode" == "--preview" ]]; then
  echo "Local preview at http://localhost:8080  (Ctrl-C to stop)"
  ( cd "$build" && python3 -m http.server 8080 )
else
  command -v fly >/dev/null || { echo "flyctl not found — install from https://fly.io/docs/flyctl/"; exit 1; }
  ( cd "$build" && fly deploy )
fi
