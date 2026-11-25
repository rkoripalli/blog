"""UI gate for the screenshot job (HOM-1136): score Impeccable findings and diff pixels, base vs PR.

Reads the PNGs and `<name>.findings.json` files written by scripts/ui_screenshots.py for each
side (shots/base, shots/pr). Per page (one shot): score = warnings x1 + errors x3, advisory
findings excluded. A PR is "regressed" when any page

  * scores higher than its base page,
  * is new (no base shot) and has a non-zero score, or
  * changes more than --threshold percent of its pixels.

No base shots at all (first UI PR, or the base run failed) means there is no baseline: the table
is still written, but nothing counts as a regression, and pixel diff is skipped.

Writes a markdown table to $GITHUB_STEP_SUMMARY (stdout when unset) and `regressed=true|false`
to $GITHUB_OUTPUT. Always exits 0: the gate labels, it never fails the PR. Only the literal
true/false and the finding type names (from the detector's own rule registry) are emitted.

Usage: python pr/scripts/ui_gate.py --base shots/base --pr shots/pr [--threshold 5]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

WEIGHTS = {"error": 3, "warning": 1}
PIXEL_TOLERANCE = 8  # per-channel difference ignored as anti-aliasing noise


def load_findings(png: Path) -> list[dict] | None:
    """Findings for one shot, or None when the scan did not produce data."""
    path = png.with_suffix(".findings.json")
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if "findings" not in data:
        return None
    return data["findings"]


def score(findings: list[dict]) -> int:
    total = 0
    for f in findings:
        if f.get("advisory") or f.get("severity") == "advisory":
            continue
        total += WEIGHTS.get(f.get("severity") or "warning", 1)
    return total


def finding_keys(findings: list[dict]) -> Counter:
    return Counter(
        (f.get("type"), f.get("selector"))
        for f in findings
        if not (f.get("advisory") or f.get("severity") == "advisory")
    )


def changed_percent(base_png: Path, pr_png: Path) -> float:
    """Percent of pixels that differ; the area outside the smaller image counts as changed."""
    from PIL import (  # imported here so the scoring half works without Pillow
        Image,
        ImageChops,
    )

    with Image.open(base_png) as a, Image.open(pr_png) as b:
        a = a.convert("RGBA")
        b = b.convert("RGBA")
        width, height = max(a.width, b.width), max(a.height, b.height)
        ca = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        cb = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ca.paste(a, (0, 0))
        cb.paste(b, (0, 0))
    diff = ImageChops.difference(ca, cb)
    mask = diff.split()[0]
    for band in diff.split()[1:]:
        mask = ImageChops.lighter(mask, band)
    mask = mask.point([0] * (PIXEL_TOLERANCE + 1) + [255] * (255 - PIXEL_TOLERANCE))
    return 100.0 * mask.histogram()[255] / (width * height)


def cell(text: str) -> str:
    return str(text).replace("|", "/").replace("\n", " ")


def run(base_dir: Path, pr_dir: Path, threshold: float) -> tuple[bool, str]:
    pr_shots = sorted(pr_dir.glob("*.png"))
    base_exists = {p.name for p in base_dir.glob("*.png")} if base_dir.is_dir() else set()
    baseline = bool(base_exists)

    rows: list[str] = []
    regressed = False
    for pr_png in pr_shots:
        name = pr_png.stem
        pr_findings = load_findings(pr_png)
        pr_score = score(pr_findings) if pr_findings is not None else None
        base_png = base_dir / pr_png.name
        base_findings = load_findings(base_png) if base_png.exists() else None
        base_score = score(base_findings) if base_findings is not None else None

        new_findings = ""
        pct = None
        reasons: list[str] = []
        if baseline and base_png.exists():
            pct = changed_percent(base_png, pr_png)
            if pct > threshold:
                reasons.append("pixels")
        if baseline and pr_findings is not None:
            if base_findings is not None:
                added = finding_keys(pr_findings) - finding_keys(base_findings)
                new_findings = ", ".join(sorted({t or "?" for t, _ in added.elements()}))
                if pr_score is not None and base_score is not None and pr_score > base_score:
                    reasons.append("score")
            elif not base_png.exists() and pr_score:
                reasons.append("new page")
                new_findings = ", ".join(sorted({t or "?" for t, _ in finding_keys(pr_findings)}))
        if reasons:
            regressed = True
        rows.append(
            f"| {cell(name)} | {'n/a' if base_score is None else base_score} "
            f"| {'n/a' if pr_score is None else pr_score} | {cell(new_findings) or '-'} "
            f"| {'n/a' if pct is None else f'{pct:.2f}%'} | {cell(', '.join(reasons)) or '-'} |"
        )

    lines = ["## UI gate (HOM-1136)", ""]
    if not pr_shots:
        lines.append("No PR screenshots found; nothing scored.")
    elif not baseline:
        lines.append("No base screenshots, so no baseline: no label. Scores shown for the PR only.")
    elif regressed:
        lines.append(f"Regression found (pixel threshold {threshold:g}%): label `ui-review`.")
    else:
        lines.append(f"No regression (pixel threshold {threshold:g}%): no label.")
    lines += [
        "",
        "Score = warnings x1 + errors x3, advisory findings excluded. n/a = no data for that side.",
        "",
        "| Page | Base score | PR score | New findings | Changed | Flag |",
        "|---|---|---|---|---|---|",
        *rows,
        "",
    ]
    return regressed, "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Score base vs PR UI screenshots (HOM-1136).")
    ap.add_argument("--base", default="shots/base")
    ap.add_argument("--pr", default="shots/pr")
    ap.add_argument("--threshold", type=float, default=5.0, help="changed-pixel percent (default 5)")
    args = ap.parse_args()

    try:
        regressed, markdown = run(Path(args.base), Path(args.pr), args.threshold)
    except Exception as exc:  # noqa: BLE001 - the gate must never fail the PR
        regressed, markdown = (
            False,
            f"## UI gate (HOM-1136)\n\nGate error, no label: `{cell(type(exc).__name__)}`\n",
        )
        print(f"ui_gate error: {exc}", file=sys.stderr)

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(markdown + "\n")
    else:
        print(markdown)
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as fh:
            fh.write(f"regressed={'true' if regressed else 'false'}\n")
    print(f"regressed={'true' if regressed else 'false'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
