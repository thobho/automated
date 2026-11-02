#!/usr/bin/env python3
"""T15: rank themes and write themes/THEMES.md from taxonomy.py + catalogue (+ build_themes helpers).

Run after build_themes.py --write:
    python3 projects/idea-generator/phase2/themes/render_themes.py
Also writes the rank and batch into themes/stats.csv.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from taxonomy import THEMES, MEMBERS  # noqa: E402
from build_themes import load, signals, hype_kinds, caveat, label, year  # noqa: E402

W_SPREAD, W_DUR, W_NOV = 0.40, 0.35, 0.25


def theme_rows():
    rows = {}
    for path, (_, rs, _) in load().items():
        for r in rs:
            r["_file"] = os.path.basename(path)
            sig = signals(r["durable_signals"])
            kinds = hype_kinds(r["hype_warnings"])
            r["_sig"], r["_hype"] = sig, kinds
            r["_label"], r["_score"] = label(sig, len(kinds))
            r["_year"] = year(r["launched"])
            r["_caveat"] = caveat(r["hype_warnings"])
            rows.setdefault(r["theme"], []).append(r)
    return rows


def assess(t, members):
    countries = sorted({r["country"] for r in members})
    regions = sorted({r["region"] for r in members}, key=lambda x: int(x[1:]))
    n = {k: sum(r["_label"] == k for r in members)
         for k in ("durable", "promising", "unproven", "hype", "no-evidence")}
    dp = n["durable"] + n["promising"]
    nh = sum(1 for r in members if r["_hype"])
    spread = 0.6 * min(len(countries), 10) / 10 + 0.4 * min(len(regions), 6) / 6
    dur = max(0.0, min(dp, 5) / 5 - 0.1 * min(nh, 3))
    nov = (t[4] - 1) / 2
    score = 100 * (W_SPREAD * spread + W_DUR * dur + W_NOV * nov)
    if dp >= 2 and nh <= dp / 2:
        verdict = "durable"
    elif nh >= 2 and nh > dp:
        verdict = "hype"
    else:
        verdict = "mixed"
    thin = n["no-evidence"] * 2 >= len(members)
    return dict(countries=countries, regions=regions, n=n, dp=dp, nh=nh, spread=spread,
                dur=dur, nov=nov, score=score, verdict=verdict, thin=thin)


def link(r):
    return f"[{r['name']}](../catalogue/{r['_file']}) `{r['id']}`"


def examples(members, k=6):
    order = sorted(members, key=lambda r: (-r["_score"], -len(r["_sig"]), r["id"]))
    picked, seen = [], set()
    for r in order:  # one per country first, best evidence first
        if r["country"] not in seen:
            picked.append(r)
            seen.add(r["country"])
        if len(picked) == k:
            return picked
    for r in order:
        if r not in picked:
            picked.append(r)
        if len(picked) == k:
            break
    return picked


def short(text, n=220):
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1].rsplit(" ", 1)[0] + " …"


def source_url(cell):
    for tok in (cell or "").split():
        if tok.startswith("http"):
            return tok.rstrip(".,;")
    return None


def main():
    rows = theme_rows()
    info = {t[0]: t for t in THEMES}
    res = []
    for t in THEMES:
        a = assess(t, rows[t[0]])
        a["t"] = t
        res.append(a)
    res.sort(key=lambda a: (-round(a["score"], 1), -len(a["countries"]), a["t"][0]))
    size = -(-len(res) // 3)
    for i, a in enumerate(res):
        a["rank"] = i + 1
        a["batch"] = "ABC"[i // size]

    L = []
    L.append("# Phase 2 themes (T15)\n")
    L.append(f"{len(res)} themes clustered from all {sum(len(v) for v in rows.values())} rows of "
             "`catalogue/*.csv` (R0-global and R1–R10). Every catalogue row carries its theme id in the "
             "`theme` column. Theme ids (TH01–TH69) are stable: later tasks refer to them; the rank may change, the id does not.\n")
    L.append("Built reproducibly: [taxonomy.py](taxonomy.py) (theme definitions, Polish angle, membership) → "
             "[build_themes.py](build_themes.py) `--write` (fills the catalogue column, writes [mapping.csv](mapping.csv) "
             "and [stats.csv](stats.csv)) → [render_themes.py](render_themes.py) (ranking and this file). "
             "To move a product, edit `MEMBERS` in taxonomy.py and rerun both scripts.\n")
    L.append("## Ranking rule\n")
    L.append("Score (0–100) = **40% spread + 35% durable traction + 25% novelty**. Raw growth, funding size and "
             "headline ARR are deliberately not inputs.\n")
    L.append("- **Spread** = 0.6 × min(countries, 10)/10 + 0.4 × min(regions, 6)/6, counting the distinct "
             "`country` and `region` values of the theme's rows (R0 rows count under their own country and region R0).")
    L.append("- **Durable traction** = min(D, 5)/5 − 0.1 × min(H, 3), floored at 0. D = members labelled "
             "*promising* or *durable*, H = members with at least one hype warning. Each member is labelled with "
             "the rubric in [criteria.md §6](../method/criteria.md): durable points = recorded signal numbers "
             "(1–10) in `durable_signals`, with 3 and 4 counted double, minus 2 × hype warnings. Hype warnings "
             "are only the brief's list (tourist spikes, one-off/lifetime revenue, paid-ads/influencer growth, "
             "novelty use case, thin wrapper, price cuts, layoffs/pivot); other text in `hype_warnings` "
             "(self-reported figures, weak traction, no LLM) is counted as a **caveat**, not hype.")
    L.append("- **Novelty** = (n − 1)/2 with n = 1–3 set per theme in taxonomy.py: 3 = LLM-native and replaces a "
             "job step or service end to end; 2 = the LLM does one real step in a familiar workflow; "
             "1 = commodity, infrastructure, classic software or a novelty use case.")
    L.append("- **Durability verdict** per theme: *durable* if D ≥ 2 and H ≤ D/2; *hype* if H ≥ 2 and H > D; otherwise "
             "*mixed*. \"thin\" marks themes where half or more of the rows have no "
             "recorded signal or warning at all.")
    L.append("- Ties: more countries first, then theme id. Batches: ranks 1–23 = **A**, 24–46 = **B**, "
             "47–69 = **C** (T16, T17, T18).\n")
    L.append("**Caveats.** (1) No member reaches the rubric's *durable* label (≥ 7 points incl. retention or "
             "expansion): the catalogue has very little retention/NRR data, so *durable* here means \"several "
             "members with ≥ 4 recorded signal points and few hype warnings\", a relative verdict. "
             "(2) Signals are counted as recorded in the catalogue; not every one carries its own URL, so T16–T18 "
             "must re-check the evidence before scoring L2. (3) Launch years are the last year written in "
             "`launched` (usually the LLM-era launch or breakout), not founding dates. (4) Spread counts where "
             "the scans found products, so regions scanned more deeply (R0/R1 US) inflate US-heavy themes "
             "less than it seems: spread caps at 10 countries and 6 regions.\n")

    L.append("## Ranked list\n")
    L.append("| Rank | Batch | Id | Theme | Rows | Countries | Regions | D | H | Verdict | Novelty | Score |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for a in res:
        t = a["t"]
        v = a["verdict"] + (" (thin)" if a["thin"] else "")
        L.append(f"| {a['rank']} | {a['batch']} | [{t[0]}](#{t[0].lower()}) | {t[1]} | {len(rows[t[0]])} | "
                 f"{len(a['countries'])} | {len(a['regions'])} | {a['dp']} | {a['nh']} | {v} | {t[4]} | {a['score']:.1f} |")
    L.append("")

    for b, task in zip("ABC", ("T16", "T17", "T18")):
        group = [a for a in res if a["batch"] == b]
        L.append(f"## Batch {b} ({len(group)} themes, Poland check {task})\n")
        for a in group:
            t = a["t"]
            ms = rows[t[0]]
            n = a["n"]
            L.append(f"### {t[0]}\n")
            L.append(f"**{a['rank']}. {t[1]}** · score {a['score']:.1f} · batch {b}\n")
            L.append(f"- **What:** {t[2]} **LLM role:** {t[3]}.")
            b2 = {}
            for r in ms:
                b2[r["b2b_b2c"]] = b2.get(r["b2b_b2c"], 0) + 1
            L.append("- **B2B/B2C:** " + ", ".join(f"{k} {v}" for k, v in sorted(b2.items(), key=lambda kv: -kv[1])) + ".")
            L.append("- **Examples:** " + "; ".join(link(r) for r in examples(ms)) + ".")
            dated = [r for r in ms if r["_year"]]
            if dated:
                e = min(dated, key=lambda r: (r["_year"], r["id"]))
                l_ = max(dated, key=lambda r: (r["_year"], r["id"]))
                when = (f"earliest {e['_year']} ({e['name']}, {e['country']}), latest {l_['_year']} "
                        f"({l_['name']}, {l_['country']}); {len(dated)}/{len(ms)} rows dated")
            else:
                when = "no launch years recorded"
            L.append(f"- **Spread:** {len(a['countries'])} countries in {len(a['regions'])} regions "
                     f"({' '.join(a['regions'])}): {', '.join(a['countries'])}. Launch/breakout: {when}.")
            best = max(ms, key=lambda r: (r["_score"], len(r["_sig"]), r["id"]))
            url = source_url(best["traction_source"])
            src = f" ([source]({url}))" if url else ""
            sig = ", ".join(str(s) for s in sorted(best["_sig"])) or "none recorded"
            L.append(f"- **Best traction:** {best['name']} ({best['country']}): {short(best['traction'])}{src}; "
                     f"durable signals recorded: {sig}.")
            hk = sorted({k for r in ms for k in r["_hype"]})
            cav = sum(r["_caveat"] for r in ms)
            L.append(f"- **Durability: {a['verdict']}{' (thin)' if a['thin'] else ''}.** Members: "
                     f"{n['promising']} promising, {n['unproven']} unproven, {n['hype']} hype, "
                     f"{n['no-evidence']} no evidence; hype warnings: {', '.join(hk) if hk else 'none'}; "
                     f"{cav} rows with caveats.")
            L.append(f"- **Polish angle (first thought):** {t[5]}")
            L.append("- **All members:** " + ", ".join(f"{r['name']} `{r['id']}`" for r in sorted(ms, key=lambda r: r["id"])) + ".")
            L.append("")

    L.append("## Coverage\n")
    L.append(f"- Catalogue rows tagged: {sum(len(v) for v in rows.values())} in 11 files; themes: {len(res)}; "
             f"batches A/B/C: {sum(a['batch']=='A' for a in res)}/{sum(a['batch']=='B' for a in res)}/{sum(a['batch']=='C' for a in res)}.")
    L.append("- Inputs also read: regional READMEs `research/regions/*/README.md` and `research/global/README.md` "
             "(their patterns informed the clustering and the Polish angles). No new web sources were added in T15; "
             "every traction link is copied from the catalogue's `traction_source` column.")
    L.append("- Smallest themes (2 rows: TH64, TH66, TH69) were kept separate rather than forced into a broader "
             "theme because their buyer and workflow differ; they rank low and sit in batch C.")
    L.append("")
    open(os.path.join(HERE, "THEMES.md"), "w", encoding="utf-8").write("\n".join(L))

    sp = os.path.join(HERE, "stats.csv")
    st = list(csv.DictReader(open(sp, encoding="utf-8")))
    by = {a["t"][0]: a for a in res}
    for s in st:
        a = by[s["theme"]]
        s.update(rank=a["rank"], batch=a["batch"], verdict=a["verdict"] + (" (thin)" if a["thin"] else ""),
                 score=f"{a['score']:.1f}", n_hype_members=a["nh"])
    st.sort(key=lambda s: int(s["rank"]))
    with open(sp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(st[0]), quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writeheader()
        w.writerows(st)
    for a in res:
        print(a["rank"], a["batch"], a["t"][0], f"{a['score']:.1f}", len(a["countries"]), a["dp"], a["nh"], a["verdict"], a["t"][1])


if __name__ == "__main__":
    main()
