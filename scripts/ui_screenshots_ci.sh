#!/usr/bin/env bash
# Build one checkout, serve it, screenshot it, stop it (HOM-752).
# Usage, from the workflow root: bash pr/scripts/ui_screenshots_ci.sh base|pr
set -euo pipefail
side="$1"
port=4321
log="server-$side.log"
export ASTRO_TELEMETRY_DISABLED=1

# Something already answering on the port would be shot instead of this side's code.
if curl -sf "http://127.0.0.1:$port/blog/" >/dev/null 2>&1; then
  echo "port-in-use-before-start: $port"; exit 1
fi

(cd "$side" && npm ci --no-audit --no-fund && npm run build)
# exec the local astro binary, so $! is the server process itself and the trap
# below actually stops it (npx would leave the real server running).
(cd "$side" && exec ./node_modules/.bin/astro preview --host 127.0.0.1 --port "$port") >"$log" 2>&1 &
pid=$!
# Wait for the server to exit so the next side never finds this one still
# answering on the port during shutdown.
trap 'kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; echo "--- $log"; tail -n 40 "$log"' EXIT

for _ in $(seq 1 60); do
  if curl -sf "http://127.0.0.1:$port/blog/" >/dev/null; then ready=1; break; fi
  kill -0 "$pid" 2>/dev/null || { echo "server exited early"; exit 1; }
  sleep 1
done
[ "${ready:-}" = 1 ] || { echo "server not ready after 60s"; exit 1; }

python pr/scripts/ui_screenshots.py --base-url "http://127.0.0.1:$port" \
  --out "shots/$side" --fixtures pr/tests/fixtures/ui
