#!/bin/sh
# Generate config.js from the environment, then serve the static frontend.
# If RXEGYPT_API_URL is set, the app runs in LIVE mode against that backend;
# otherwise it falls back to the committed config.js (DEMO mode).
set -e

if [ -n "$RXEGYPT_API_URL" ]; then
  printf "window.RXEGYPT_API_URL = '%s';\n" "$RXEGYPT_API_URL" > /app/config.js
  echo "config.js -> LIVE mode: $RXEGYPT_API_URL"
else
  echo "config.js -> DEMO mode (no RXEGYPT_API_URL set)"
fi

exec python -m http.server 3000
