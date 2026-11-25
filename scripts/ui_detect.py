"""Impeccable detector helper for the UI screenshot scripts (HOM-1136).

The vendored detector (scripts/vendor/impeccable-detect.js, hash-pinned, see
scripts/vendor/README.md) is injected into each Playwright page. After the page has rendered,
`scan_page` runs it and writes `<shot>.findings.json` next to the PNG; scripts/ui_gate.py scores
those files, base vs PR.

Usage inside a screenshot script, per page state:

    from ui_detect import DETECTOR_CONFIG, load_detector, scan_page

    detector_js = load_detector()                 # once per run
    context.add_init_script(DETECTOR_CONFIG)      # before the page loads
    ...
    page.add_script_tag(content=detector_js)      # after goto, before the screenshot
    page.screenshot(path=str(shot), full_page=True)
    scan_page(page, shot)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
DETECTOR = SCRIPTS / "vendor" / "impeccable-detect.js"
DETECTOR_SHA256 = "4f053a88a8de1d28630972720ca605ffbbd4c9eb8990e5b1d1eac31ea5256af9"
# autoScan off: the gate triggers the scan itself, once per shot, after the page has rendered.
DETECTOR_CONFIG = "window.__IMPECCABLE_CONFIG__ = { autoScan: false };"
IMPECCABLE_CONFIG = REPO_ROOT / ".impeccable" / "config.json"


def load_detector() -> str:
    """Read the vendored detector and refuse to use it if the hash does not match."""
    data = DETECTOR.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != DETECTOR_SHA256:
        raise SystemExit(f"detector-hash-mismatch: {DETECTOR} is {digest}, expected {DETECTOR_SHA256}")
    return data.decode("utf-8")


def ignored_rules() -> set[str]:
    """Rule ids the repo ignores in `.impeccable/config.json` (detector.ignoreRules)."""
    try:
        data = json.loads(IMPECCABLE_CONFIG.read_text(encoding="utf-8"))
        return {str(r) for r in data.get("detector", {}).get("ignoreRules", [])}
    except (OSError, ValueError, AttributeError):
        return set()


def scan_page(page, shot: Path) -> None:
    """Run the detector on the current page state; write <shot>.findings.json beside the PNG.

    A scan failure must never lose the screenshot, so it is recorded as an error file the gate
    treats as "no data" for that page."""
    target = shot.with_suffix(".findings.json")
    skip = ignored_rules()
    try:
        groups = page.evaluate("() => window.impeccableDetect({decorate: false, serialize: true})")
        findings = [
            {
                "type": f.get("type"),
                "severity": f.get("severity") or "warning",
                "advisory": bool(f.get("advisory")),
                "selector": g.get("selector", ""),
            }
            for g in groups
            for f in g.get("findings", [])
            if f.get("type") not in skip
        ]
        target.write_text(json.dumps({"findings": findings}), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - informational job, keep shooting
        target.write_text(json.dumps({"error": str(exc)[:200]}), encoding="utf-8")
