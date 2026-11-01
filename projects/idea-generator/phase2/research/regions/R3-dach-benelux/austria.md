# Austria (T07)

All sources accessed **2026-11-01**. "Read" = page opened; "excerpt" = search summary only (unverified). Catalogue rows R3-AT-001…005 in [../../../catalogue/R3-dach-benelux.csv](../../../catalogue/R3-dach-benelux.csv). Searches in German (Trending Topics, regional press) and English. brutkasten blocks bots (per [countries.md](../../../method/countries.md)) and was not used.

Context: Austrian startups raised 472M EUR in H1 2026, more than three times the prior-year period ([Börse Express](https://www.boerse-express.com/news/articles/oesterreich-start-ups-472-millionen-euro-finanzierung-im-halbjahr-925811), excerpt).

## Findings

| # | Product | What it does | Traction (date) | Source | Polish angle |
|---|---|---|---|---|---|
| AT-001 | **fonio.ai** (Vienna) | AI phone assistants that take customer calls; vertical pages for Arztpraxen and others | Seed >17M USD (~14.7M EUR) led by 20VC, "second-largest seed round in Austrian startup history"; >3M EUR angel round 2025-12; founded autumn 2024; 7,500+ customers (VW, BRITA, Hagebau); 2M+ calls/month automated (company) (read, article 2026-06-09) | [vienna.at](https://www.vienna.at/dieses-wiener-startup-soll-millionen-telefonate-uebernehmen/10238927) | Polish SMB/clinic voice receptionist; fonio publishes content in several languages (de/nl/es pages seen in search), so it can enter PL with a translation. Peers in R0: telli, Synthflow (Berlin) |
| AT-002 | **Lohnbot** (Vienna) | Payroll automation that lets firms bring Lohnverrechnung in-house: calculations, reports to ÖGK, tax office and adviser. AI **planned**: collective-agreement changes, cost forecasts, employee chatbot | 750+ companies (≈250 a year earlier); 10 EUR per employee/month; FFG grant 280k EUR; Germany planned for 2025 (read, article 2024-02-12) | [Trending Topics](https://www.trendingtopics.eu/lohnbot-lohnverrechnung-per-mausklick-expandiert-ins-ausland/) | Payroll is deeply national (ZUS DRA/RCA, PIT-11, PPK, układy zbiorowe, minimum wage changes). An LLM that reads rule changes and answers employee payslip questions is the new layer |
| AT-003 | **XUND** (Vienna) | MDR-certified symptom and health checks for insurers, hospitals, pharma; medical LLM ("RAVE") and an assistant on Mistral models | Pre-Series A 6M EUR (Lead Ventures, J&T Ventures), 2025-03-05 (read); insurers hkk and AOK NordWest's app (~3M insured) and Wiener Städtische embed it ([xund.ai](https://xund.ai/), company claim, excerpt) | [Trending Topics](https://www.trendingtopics.eu/xund-investment-2025/) | B2B2C via insurers; in PL the buyers would be abonament providers (Medicover, LUX MED) and insurers. Medical-device certification is an L7 problem |
| AT-004 | **Propcorn** (Vienna) | Address search that shows plot size, building class, zoning, protection status, and AI-estimated buildable area, extra floors or attic potential; downloadable report | Pre-seed 600k EUR (Hansi Hansmann's Hans(wo)men Group, Calm/Storm, Weilburg Ventures), 2024-09-05 (read) | [Trending Topics](https://www.trendingtopics.eu/propcorn-600-000-euro-in-pre-seed-runde-fuer-neue-ki-basierte-immobilienplattform/) | **Strong local-data analogue:** plot-potential report from MPZP / warunki zabudowy + EGiB + Geoportal + KW for developers, pośrednicy, investors (see R2 Orbital/Moverly) |
| AT-005 | **goai** (Linz) | Custom AI phone assistant answering from a business's knowledge base, handing complex calls to staff; 25 languages | Founded mid-2025; several DACH SMB customers, often doctors' practices booking appointments; AI handles ~80% of inquiries alone (company) (read, 2026-01-14) | [MeinBezirk](https://www.meinbezirk.at/linz/c-wirtschaft/linzer-start-up-goai-will-kundenservice-revolutionieren_a7957935) | Evidence that SMB voice agents are crowded in DACH (fonio, goai, fluently, telli, Synthflow) |

Not catalogued: **Studo** (student organiser) and **Lingvano** (Austrian sign-language app) appear in the AT top-grossing Education chart but are not LLM products; **fluently** (Linz voice assistant; excerpt only).

## App Store charts (top-grossing AT, 2026-11-01)
Local or country-specific in the top 25: Studo (#6 Education), Lingvano (ÖGS sign language, #7 Education), Finanzguru (#1 Finance, German), Fahrtenbuch apps (Driversnote, Tripbook), "Spesen und Reisekosten" (Finance), MyGEWO (Lifestyle, housing-association app). LLM-era apps are the global ones plus German-language chatbot wrappers.

## Patterns (Austria)
1. **Vienna is a voice-agent hub**: fonio's 20VC-led seed and 7,500 customers in under two years is the strongest SMB voice traction in the region; goai and fluently follow. Combined with Berlin's telli and Synthflow (R0), DACH SMB voice is crowded; the Polish window depends on Polish-language voice quality and clinic/booking integrations, not on the idea.
2. **Address-level property intelligence** (Propcorn) is the Austrian contribution to the registry-plus-AI theme from R2 (Orbital, Moverly).
3. **Payroll tools add AI late**: Lohnbot (like plancraft in Germany) promises AI on top of a rules engine; the durable value is the national rule set.

## Coverage (Austria)
- Products: 5 catalogued (meets ≥5); none of R0–R2 is Austrian-based. Seen, not catalogued: Studo, Lingvano, fluently, MyGEWO (4). Products researched: 9.
- Sources read: 5 pages + 6 App Store feeds.
- Searches: 4 ("österreichisches KI-Startup Finanzierung Steuerberater Anwälte Verwaltung", "XUND", "goai Linz", "Lohnverrechnung KI" via the German payroll search).
- Found nothing: Austrian LLM startups for Steuerberater, Anwälte, FinanzOnline filings or public administration with traction; Lohnbot's AI features actually shipped; Propcorn traction after pre-seed.
