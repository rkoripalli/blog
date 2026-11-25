# Vendored: Impeccable browser detector

`impeccable-detect.js` is the Impeccable anti-pattern detector for the browser, copied
byte-for-byte and not edited. It is injected into the Playwright pages in
`scripts/ui_detect.py`, and `scripts/ui_gate.py` scores the findings (HOM-1136).

| | |
|---|---|
| Upstream | https://github.com/pbakaus/impeccable (plugin `impeccable` 4.0.4, `skills/impeccable/scripts/detector/detect-antipatterns-browser.js`) |
| Copyright | (c) 2026 Paul Bakaus |
| License | Apache-2.0, text in `LICENSE-impeccable` |
| sha256 | `4f053a88a8de1d28630972720ca605ffbbd4c9eb8990e5b1d1eac31ea5256af9` |

`ui_detect.py` checks the sha256 before injecting and stops if it does not match.
The file makes no network calls (no `fetch`, XHR or WebSocket).

## Updating

1. Copy the new `detect-antipatterns-browser.js` over `impeccable-detect.js`.
2. Update the version and sha256 above and `DETECTOR_SHA256` in `scripts/ui_detect.py`.
3. Open a PR; the UI screenshots job renders base vs PR with the new detector.
