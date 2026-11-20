#!/usr/bin/env bash
# Post-deploy smoke check (HOM-1134).
# Status codes only: never reads or logs a response body, never follows redirects.
#
#   deploy-smoke.sh check BASE_URL /path=CODE [/path=CODE ...]
#       Requests BASE_URL+path and compares the HTTP status. Failing URLs and
#       statuses go to the failures file. Exit 1 if any check still fails after
#       SMOKE_RETRIES attempts (default 1, SMOKE_RETRY_DELAY seconds apart).
#
#   deploy-smoke.sh issue
#       Opens (or comments on) a GitHub issue labelled deploy-smoke with the
#       contents of the failures file. Needs GITHUB_TOKEN and GITHUB_REPOSITORY.
#       The body holds URLs, statuses, the short commit and the run link only.
set -u

FAIL_FILE="${SMOKE_FAIL_FILE:-${RUNNER_TEMP:-/tmp}/deploy-smoke-failures.txt}"

check() {
  base="${1%/}"
  shift
  attempts="${SMOKE_RETRIES:-1}"
  delay="${SMOKE_RETRY_DELAY:-10}"
  for attempt in $(seq 1 "$attempts"); do
    : > "$FAIL_FILE"
    for spec in "$@"; do
      path="${spec%=*}"
      want="${spec##*=}"
      got=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$base$path") || got=000
      if [ "$got" = "$want" ]; then
        echo "ok   $got $base$path"
      else
        echo "FAIL $got (want $want) $base$path"
        echo "$base$path got $got, want $want" >> "$FAIL_FILE"
      fi
    done
    if [ ! -s "$FAIL_FILE" ]; then
      echo "Smoke OK"
      return 0
    fi
    if [ "$attempt" -lt "$attempts" ]; then
      echo "Smoke attempt $attempt/$attempts failed, retrying in ${delay}s"
      sleep "$delay"
    fi
  done
  return 1
}

issue() {
  [ -s "$FAIL_FILE" ] || { echo "No failures file, nothing to report"; return 0; }
  FAIL_FILE="$FAIL_FILE" python3 - <<'PY'
import json
import os
import urllib.request

repo = os.environ["GITHUB_REPOSITORY"]
token = os.environ["GITHUB_TOKEN"]
failures = open(os.environ["FAIL_FILE"], encoding="utf-8").read().strip()
sha = os.environ.get("GITHUB_SHA", "")[:7]
run_url = "{}/{}/actions/runs/{}".format(
    os.environ.get("GITHUB_SERVER_URL", "https://github.com"), repo, os.environ.get("GITHUB_RUN_ID", "")
)
body = "Post-deploy smoke check failed for commit {}.\n\n```\n{}\n```\n\nRun: {}\n".format(sha, failures, run_url)


def api(method, path, data=None):
    req = urllib.request.Request(
        "https://api.github.com/repos/{}/{}".format(repo, path),
        data=json.dumps(data).encode() if data is not None else None,
        method=method,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


existing = api("GET", "issues?labels=deploy-smoke&state=open&per_page=1")
if existing:
    api("POST", "issues/{}/comments".format(existing[0]["number"]), {"body": body})
    print("Commented on issue #{}".format(existing[0]["number"]))
else:
    created = api(
        "POST",
        "issues",
        {"title": "Deploy smoke check failed ({})".format(sha), "body": body, "labels": ["deploy-smoke"]},
    )
    print("Opened issue #{}".format(created["number"]))
PY
}

case "${1:-}" in
  check) shift; check "$@" ;;
  issue) issue ;;
  *) echo "usage: $0 check BASE_URL /path=CODE ... | issue" >&2; exit 2 ;;
esac
