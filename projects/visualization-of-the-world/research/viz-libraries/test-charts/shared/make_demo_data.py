#!/usr/bin/env python3
"""Generate shared/demo-data.json: SYNTHETIC demo values for the library test charts.
Nothing here is real demography; values are deterministic pseudo-data (no randomness)."""
import json, math, pathlib
here = pathlib.Path(__file__).parent
years = list(range(2000, 2026))
series = ["Series A (demo)", "Series B (demo)", "Series C (demo)"]
line = {s: [round(100 + 18*i*(k+1)/5 + 12*math.sin(y/3 + k*2), 1) for y in years for i in [y-2000]] for k, s in enumerate(series)}
cats = ["Group 1", "Group 2", "Group 3", "Group 4", "Group 5"]
stacks = ["Class X (demo)", "Class Y (demo)", "Class Z (demo)"]
bars = {str(y): {st: [round(20 + 6*c + 3*k*(y-2000)/5 + 4*math.sin(y/2 + c + k), 1) for c in range(5)]
                 for k, st in enumerate(stacks)} for y in years}
teryt = ["02","04","06","08","10","12","14","16","18","20","22","24","26","28","30","32"]
choropleth = {t: round(40 + 55*abs(math.sin(int(t)*1.7)), 1) for t in teryt}
out = {"_note": "SYNTHETIC DEMO DATA for library tests, not real statistics.",
       "years": years, "line": {"series": line}, "bars": {"categories": cats, "stacks": stacks, "byYear": bars},
       "choropleth": {"unit": "demo index (0-100)", "byTeryt": choropleth}}
(here / "demo-data.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
