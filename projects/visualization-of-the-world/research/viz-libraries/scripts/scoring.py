#!/usr/bin/env python3
"""Weighted scoring matrix for the visualization-library choice (issue #12).

Scores are 0-5 judgements; the evidence for each is in report.md (cited as [S#] in sources.md).
Run: python3 scripts/scoring.py          -> prints the markdown matrix used in report.md
"""
CRITERIA = [  # (key, short label, weight)
    ("polish", "Visual polish and styling", 15),
    ("dynamic", "Dynamic features", 15),
    ("maps", "Maps (choropleth, points, drill-down, 2.5k shapes)", 20),
    ("formats", "Input/output formats", 8),
    ("docs", "Docs and community", 7),
    ("agent", "Agent-friendliness", 10),
    ("licence", "Licence", 8),
    ("maint", "Maintenance health", 7),
    ("bundle", "Bundle size and no-build", 5),
    ("a11y", "Accessibility, touch, mobile", 5),
]
# order: polish dynamic maps formats docs agent licence maint bundle a11y
SCORES = {
    "Apache ECharts":        [4, 5, 4, 4, 4, 5, 5, 4, 3, 4],
    "D3 + Observable Plot":  [4, 3, 4, 5, 4, 3, 5, 3, 4, 3],
    "Vega-Lite (+Vega)":     [3, 4, 4, 5, 4, 4, 5, 5, 3, 3],
    "Plotly.js":             [3, 4, 3, 3, 5, 4, 5, 5, 1, 3],
    "Highcharts":            [5, 4, 4, 4, 5, 3, 0, 5, 4, 4],
    "Chart.js":              [3, 3, 1, 3, 4, 4, 5, 4, 5, 2],
    "amCharts 5":            [5, 5, 5, 4, 4, 4, 2, 5, 3, 3],
    "deck.gl":               [4, 4, 4, 4, 4, 3, 5, 5, 1, 2],
    "MapLibre GL JS":        [5, 4, 5, 4, 4, 3, 5, 5, 3, 4],
    "Leaflet":               [3, 3, 4, 4, 5, 4, 5, 2, 5, 4],
    "OpenLayers":            [3, 3, 5, 5, 4, 3, 5, 5, 2, 3],
}
# Gate: free for commercial use without mandatory branding or paid licence on a public site.
GATE_FAIL = {"Highcharts": "paid licence for public websites", "amCharts 5": "free tier forces the amCharts logo"}
# Libraries that draw maps only (no bar/line charts) and so cannot be the single library.
MAP_ONLY = {"deck.gl", "MapLibre GL JS", "Leaflet", "OpenLayers"}


def total(scores):
    assert len(scores) == len(CRITERIA)
    return sum(s * w for s, (_, _, w) in zip(scores, CRITERIA)) / 5.0  # 0..100


def ranking():
    return sorted(((total(v), k) for k, v in SCORES.items()), reverse=True)


def markdown():
    head = "| Library | " + " | ".join(f"{l} ({w})" for _, l, w in CRITERIA) + " | Total /100 | Note |"
    sep = "|---" * (len(CRITERIA) + 3) + "|"
    rows = []
    for t, k in ranking():
        note = ("FAILS gate: " + GATE_FAIL[k]) if k in GATE_FAIL else ("map only" if k in MAP_ONLY else "")
        rows.append(f"| {k} | " + " | ".join(str(s) for s in SCORES[k]) + f" | {t:.0f} | {note} |")
    return "\n".join([head, sep] + rows)


if __name__ == "__main__":
    print(markdown())
