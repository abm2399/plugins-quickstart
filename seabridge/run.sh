#!/usr/bin/env bash
# One-step local runner for the SeaBridge dashboard (macOS / Linux).
#
#   ./run.sh              # sample provider (offline, no pip installs)
#   ./run.sh yfinance     # live prices (needs: pip install -r requirements.txt)
#   PORT=9000 ./run.sh    # override port
#
# Starts the price service, waits for it, opens the dashboard in your browser,
# and stops the service cleanly on Ctrl+C.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HTML="$(cd "$SCRIPT_DIR/.." && pwd)/seabridge_dashboard_v2.html"
PORT="${PORT:-8787}"
export PRICE_PROVIDER="${PRICE_PROVIDER:-${1:-sample}}"
export PORT

PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
  echo "Error: Python 3 not found on PATH." >&2
  exit 1
fi

echo "Starting SeaBridge price service (provider=$PRICE_PROVIDER, port=$PORT)…"
"$PY" "$SCRIPT_DIR/server.py" &
SRV=$!

cleanup() {
  trap - EXIT INT TERM   # run once, even though multiple signals may fire
  echo
  echo "Stopping price service…"
  kill "$SRV" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Wait for the service to answer (poll, then fall back to a short sleep).
if command -v curl >/dev/null 2>&1; then
  for _ in $(seq 1 20); do
    curl -s "http://localhost:$PORT/api/prices?tickers=NVDA" >/dev/null 2>&1 && break
    sleep 0.3
  done
else
  sleep 2
fi

# Default port matches the HTML's built-in default, so only add ?api if overridden.
URL="file://$HTML"
if [ "$PORT" != "8787" ]; then
  URL="file://$HTML?api=http://localhost:$PORT/api/prices"
fi

echo "Opening dashboard: $URL"
case "$(uname -s)" in
  Darwin) open "$URL" 2>/dev/null || echo "Open it manually: $URL" ;;
  Linux)  xdg-open "$URL" >/dev/null 2>&1 || echo "Open it manually: $URL" ;;
  *)      echo "Open it manually in your browser: $URL" ;;
esac

echo "Service running at http://localhost:$PORT — press Ctrl+C to stop."
wait "$SRV"
