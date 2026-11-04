# TH32 — Tender and bid writing (Poland check)

Theme: [THEMES.md#th32](../../themes/THEMES.md#th32) · rank 28, batch B · sources accessed **2026-11-04** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Minerva (Poznań) | AI platform for bidders: scans ~5,000 tenders/day from 1,000+ sources, profiles them, supports bid documentation | not published | **115 clients**, 383 tenders won worth 250M+ PLN; USD 3M from Open Ocean (article 2025-10-16) | [xyz.pl](https://xyz.pl/dzieje-sie/startup-minerva-pozyskal-3-mln-dolarow-rozwija-technologie-ulatwiajaca-start-w-przetargach-3050) |
| Mimira | End-to-end tender automation: matching, documents, pricing, contact with the contracting authority; AI plus experts; "first bid the same day" | not published | 4M PLN round led by Elder Gull (UK), 2026-03; Zarys International's 30-person tender team uses it | [ITwiz 2026-03-03](https://itwiz.pl/mimira-z-4-mln-zl-na-cyfryzacje-przetargow-publicznych/) |
| PrzetargPro | SWZ analysis, competitor bid history, win-chance estimate; monitors BZP and TED | not checked | Product Hunt listing | [Product Hunt](https://www.producthunt.com/p/przetargpro) |
| Przetargi.io (with Softiq) | AI analysis of public construction tenders, LlamaIndex case study | not checked | not stated | [LlamaIndex/Softiq case study](https://www.plushcap.com/content/llamaindex/blog/llamaindex-case-study-tender-rfp-agent-for-construction-sector-with-softiq) |
| Training market | PARP-listed courses on AI for SWZ summaries and evaluation criteria | per course | procurement staff | [PARP BUR course](https://uslugirozwojowe.parp.gov.pl/wyszukiwarka/uslugi/drukuj-pdf?id=3701658) |

Plus classic tender search services (BIP/BZP aggregators) that autocomplete shows people already use.

## 2. Does the Western leader already serve Poland?
- **AutogenAI** (UK), **Brainial** (NL), **Cato** (IT), **Brickanta** (SE): demo-led, built around their own procurement portals and languages; no Polish site, partner or customer found in this check. Not tried hands-on (demo only).
- The gap a foreign entrant would face (BZP/e-Zamówienia, JEDZ, Pzp, KIO case law) is already being filled by funded Polish startups.

## 3. Polish demand signals
- Autocomplete (2026-11-04): "przetargi ai" → "ai przetargi publiczne", "przetargi z ai", "**minerva przetargi ai**", "**asystent ai przetargi**"; "wyszukiwarka przetargów" → 10 incl. "ai", "darmowa", "budowlanych", "unijnych"; "jedz wypełnienie" → 5 (online, espd, instrukcja); "analiza swz" → none.
- Branded searches for Minerva show the category is known in Poland.

## 4. What adaptation needs
e-Zamówienia platform and BZP notices, JEDZ/ESPD, Pzp (2019 act) and KIO rulings via M29 SAOS, M20 BIP for below-threshold notices, M09 KRS/M10 CEIDG for wykonawca documents, M52 Polish legal language. Public tenders are excluded as a sales channel, but the buyers here are private bidders, which is allowed.

## 5. Demographic or social driver
None specific. KPO/EU-funds spending and defence procurement raise tender volume (not quantified here).

## 6. CEE check
No CZ/SK/RO/HU tender AI in R6 ([R6 catalogue](../../catalogue/R6-cee-peers.csv)).

## 7. Verdict: **taken**
Two VC-backed Polish startups (Minerva with 115 clients and Mimira) plus smaller SWZ analysers already do AI tender matching and bid preparation in Polish, with branded search demand. A solo founder would enter third or fourth in a niche of professional bidders.

**Seed idea (residue, weak):** none beyond batch A's KIO-ruling monitor (TH07). A vertical bid-writer for one sector (e.g. cleaning or catering tenders below threshold) is possible but would compete with Minerva's generic platform.
