"""Render blog screenshots (HOM-752, rollout of the HOM-664 pilot).

Used by .github/workflows/ui-screenshots.yml to produce before/after PNGs for UI
review, and runnable locally the same way:

    pip install playwright && python -m playwright install chromium
    npm ci && npm run build && npx astro preview --host 127.0.0.1 --port 4321   # other shell
    python scripts/ui_screenshots.py --base-url http://127.0.0.1:4321 \
        --out shots/local --fixtures tests/fixtures/ui

Pages come from tests/fixtures/ui/pages.json. The site is static and public, so no
data is faked; requests to any host other than the local server and the Google
Fonts CDN the pages already use are aborted. A page that answers 4xx/5xx (for
example a post that does not exist on the PR base) is skipped with a warning.
"""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright
from ui_detect import DETECTOR_CONFIG, load_detector, scan_page

# The theme loads Barlow Condensed / IBM Plex from Google Fonts, so those two
# hosts are on the allow-list on purpose (HOM-752 review); everything else is blocked.
ALLOWED_HOSTS = {"127.0.0.1", "localhost", "fonts.googleapis.com", "fonts.gstatic.com"}
VIEWPORTS = {
    "desktop": dict(viewport={"width": 1440, "height": 900}),
    "mobile": dict(viewport={"width": 390, "height": 844}, is_mobile=True,
                   has_touch=True, device_scale_factor=2),
    "wide": dict(viewport={"width": 1920, "height": 1080}),
}


def route(r):
    host = urlsplit(r.request.url).hostname
    return r.continue_() if host in ALLOWED_HOSTS else r.abort()


def shoot(browser, base_url, out, page_def, viewport, detector_js) -> bool:
    name = f"{page_def['name']}-{viewport}.png"
    ctx = browser.new_context(locale="en-US", timezone_id="America/Chicago",
                              **VIEWPORTS[viewport])
    ctx.add_init_script(DETECTOR_CONFIG)
    try:
        page = ctx.new_page()
        page.route("**/*", route)
        resp = page.goto(base_url.rstrip("/") + page_def["path"], wait_until="networkidle")
        if resp is None or resp.status >= 400:
            print(f"skip {name}: HTTP {resp.status if resp else 'none'}")
            return False
        page.evaluate("document.fonts.ready")
        page.wait_for_load_state("networkidle")
        page.add_script_tag(content=detector_js)
        page.screenshot(path=str(out / name), full_page=True, animations="disabled")
        scan_page(page, out / name)
        print(f"wrote {out / name}")
        return True
    finally:
        ctx.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="Render blog screenshots.")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--fixtures", required=True, type=Path)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    pages = json.loads((a.fixtures / "pages.json").read_text(encoding="utf-8"))["pages"]
    written = 0
    detector_js = load_detector()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for page_def in pages:
                for viewport in VIEWPORTS:
                    written += shoot(browser, a.base_url, a.out, page_def, viewport, detector_js)
        finally:
            browser.close()
    return 0 if written else 1


if __name__ == "__main__":
    sys.exit(main())
