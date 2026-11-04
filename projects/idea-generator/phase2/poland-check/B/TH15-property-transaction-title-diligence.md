# TH15 — Property transaction and title diligence (Poland check)

Theme: [THEMES.md#th15](../../themes/THEMES.md#th15) · rank 24, batch B · sources accessed **2026-11-04** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Pewny Lokal | Human legal and technical audits of resale flats and plots; legal audit covers the flat's, building's and land's księgi wieczyste plus EGiB match, mortgages and easements; no AI mentioned | not on the page read; a search excerpt quoted 499 PLN for the basic plot package (unverified) | buyers of flats and plots | [pewnylokal.pl/ksiegi-wieczyste](https://pewnylokal.pl/ksiegi-wieczyste) |
| OnGeo "Raport o terenie" | Automated PDF plot report from spatial data (MPZP, utilities, hazards, prices) in ~5 minutes; free for architects; business accounts and point packages | priced by topics and plot size (figures not found) | estate agents, architects, investors | [OnGeo blog: report instructions](https://blog.ongeo.pl/instrukcja-generowanie-raportu); [OnGeo for agents](https://www.blog.ongeo.pl/raport-o-terenie-narzedzie-dla-posrednikow) |
| e-mapa.net "Raport planistyczny" | Automated zoning report per plot (MPZP, plan ogólny, registers) | 20 PLN per report (search excerpt) | plot buyers | [e-mapa.net](https://e-mapa.net/DzialkaRaport/start/mpzp.php) |
| mObywatel "Księgi wieczyste" (state) | Since spring 2026: finds KW linked to the user's PESEL, shows basic data, orders odpis/wyciąg in-app; **only own properties** | free / court fees | owners | [Spider's Web 2026-04](https://spidersweb.pl/2026/04/mobywatel-ksiegi-wieczyste.html) |
| Energent.ai (foreign, generic) | Polish landing page for AI legal due diligence (lease abstraction, title documents); not KW-specific, no Polish customers found | not found | not found | [energent.ai PL page](https://www.energent.ai/use-cases/pl/legal-due-diligence) |

No Polish product that **reads** a księga wieczysta (działy I–IV) and explains risks with an LLM was found in two Polish searches. The professional valuers' federation (PFSRM) published a 2026 AI newsletter describing AI-assisted commercial due diligence with KW review as the step "requiring great precision", i.e. still done by hand ([PFSRM newsletter 2026-04](https://psrwn.pl/wp-content/uploads/2026/04/2026_04_PFSRM_ZESPOL_ds_AI_newsletter-nr-1.pdf)).

## 2. Does the Western leader already serve Poland?
- **Orbital** (UK): site offers only US and GB country selectors, commercial real estate, demo-led; 5,000+ professionals, 250,000+ transactions/year; logos include DLA Piper and A&O Shearman (both have Warsaw offices, but nothing indicates Polish-law use). **Not in PL.** ([orbital.tech](https://www.orbital.tech/))
- **Moverly, Conveyd** (UK) are built on the UK conveyancing process (property packs, Land Registry); **Beglaubigt.de** (DE) on German notarial certification; **Paraito** (CA) on Canadian title. None localisable without rebuilding.
- Could not check: signup flows (all demo-led).

## 3. Polish demand signals
- Autocomplete (2026-11-04): "sprawdzenie księgi wieczystej" → 10 suggestions incl. "po numerze", "za darmo", "po adresie", "po numerze działki", "mieszkania" (strong consumer volume); "mapa mpzp" → 10 city variants; "due diligence nieruchomości" → 10 incl. "wzór", "cena", "kurs", "szkolenie"; "analiza księgi wieczystej" and "sprawdzenie nieruchomości przed zakupem" → none.
- People search for **access** to KW (number, address) rather than **interpretation**; the state's mObywatel feature answers part of the access need for owners.
- Apify lists a commercial EKW scraper, i.e. someone pays for KW data at scale ([Apify EKW scraper](https://apify.com/regdata/ekw-ksiegi-wieczyste-scraper?fpr=data)).

## 4. What adaptation needs
M27 EKW (no public API; KW number needed; odpisy paid), M28 Geoportal/ULDK parcels and MPZP, M14 TERYT, M09 KRS for corporate sellers, M52 Polish legal language (działy, wzmianki, hipoteka przymusowa, służebność przesyłu, roszczenia), Ustawa o księgach wieczystych i hipotece, plan ogólny gminy reform (new planning regime from 2026), notarial practice. A foreign entrant would have to rebuild everything; this is a strong data moat but also a reason KW reading is rarely automated.

## 5. Demographic or social driver
DD10: 208k completions in 2025 and mortgage lending +27% y/y (Q2 2026) mean more first-time buyers and resale checks; DD9 suburban plot buying drives MPZP/plot checks.

## 6. CEE check
No CZ/SK/RO/HU property-diligence AI in R6 ([R6 catalogue](../../catalogue/R6-cee-peers.csv)).

## 7. Verdict: **open gap**
Automated spatial reports exist (OnGeo, e-mapa) but nobody turns a KW odpis plus EGiB/MPZP into a plain-language risk report; that step is done by lawyers and auditors for hundreds of PLN. Western leaders are bound to UK/US conveyancing. Risks: buyers rely on notaries and banks for free checks, and KW access is manual (no API), so volume needs the buyer to supply the KW number or odpis PDF.

**Seed idea:** "Czy ta księga jest czysta?" — upload a KW odpis (PDF from EKW or mObywatel) or paste the number; the tool reads działy I–IV, the building and land KW, and cross-checks EGiB/MPZP via Geoportal, then returns a risk list (hipoteki, służebności, roszczenia, wzmianki, mismatched area) at 49–99 PLN per property; B2B tier for estate agents and mortgage brokers per report.
