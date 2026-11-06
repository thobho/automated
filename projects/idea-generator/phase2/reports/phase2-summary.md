# Phase 2 summary: innovative LLM products to adapt for Poland

Written 2026-11-06 by T25. It summarises T01–T24 of Phase 2. Every number below is counted from the files on this branch, and the counting method is given next to it. Estimates are marked as estimates. A Polish version for phone reading is in [podsumowanie-pl.md](podsumowanie-pl.md).

**Bottom line.** Phase 2 found more innovative ideas than Phase 1, but no stronger ones. After the skeptical review (T24) only one idea, [011 Submission and OWU comparison agent for small SME-lines brokers](../ideas/sme-ops/011-broker-owu-comparison.md) (weighted 3.2), stays in the `5–15%` band of reaching 10,000 PLN MRR within 12 months. Every other reviewed idea is `<5%`. Of the 24 write-ups, 10 were rejected or merged. The review kept finding the same two things: a Polish incumbent or platform owner already ships the feature or is one release away (Comarch, Wolters Kluwer, Docplanner, Allegro), or the state gives the same help for free (MOS 2.0, mObywatel, e-mapa, Twój e-PIT). No idea justifies building before a test. The next month should go on the five cheap validation tests in section 4, not on code. If all five fail, stop desk research and switch to customer interviews (section 9).

## 1. Method in 5 lines
1. Poland baseline: demography (50 findings, 12 demand drivers), the AI landscape and an inventory of 53 local moats ([research/poland/](../research/poland/demography.md)) (T02–T03).
2. Global trend lists plus regional scans of 51 developed countries in 10 regions, searched in English, Polish and local languages. Each product went into a catalogue row with its traction, durable signals and hype warnings (T04–T14).
3. 531 products were clustered into 69 themes, ranked by spread, durable traction and novelty ([THEMES.md](../themes/THEMES.md), T15). Each theme then got a Poland gap verdict: open, partial or taken (T16–T18).
4. 167 adaptation ideas ([longlist.md](../ideas/longlist.md)) → 59 quick-scored ([shortlist.csv](../ideas/shortlist.csv)) → 24 full write-ups with separate opportunity and risk lists (T19–T23) → an independent devil's-advocate review that re-scored all 24 (T24).
5. Nine lenses, weighted per [criteria.md](../method/criteria.md), give a score. The score maps to a chance band, and the band then moves down one step if risks outweigh opportunities by 6 or more, or if there is an unmitigated high × high risk (§4). That rule moved 13 of the 14 surviving ideas from `5–15%` to `<5%`.

## 2. Stats

**Coverage** (counted with Python `csv` over `catalogue/*.csv`, and from [countries.md](../method/countries.md)):

| Item | Count | How counted |
|---|---|---|
| Countries covered | 51 of 51 | distinct `country` values in the catalogue; all 51 marked done in countries.md |
| Countries with fewer than 5 products (reason stated) | 11 | LU, IS, GR, MT, CY, SI, HR, QA, KW, BH, CR (countries.md) |
| Products catalogued | 531 | 104 global (R0) + 427 regional rows |
| B2B / B2C / B2B2C / B2G | 387 / 112 / 29 / 3 | `b2b_b2c` column |
| Rows where "works in Polish" is unknown | 421 of 531 (79%) | `works_in_polish` = `unknown` |
| Themes | 69 | TH01–TH69 in THEMES.md |
| Poland gap verdicts | 7 open, 30 partial, 32 taken | totals in the README of [A](../poland-check/A/README.md), [B](../poland-check/B/README.md), [C](../poland-check/C/README.md) |
| Distinct source URLs | 2,305 | `grep -oE 'https?://…' \| sort -u` over all Phase 2 files, trailing punctuation stripped; includes chart and source-list URLs in method/. Per folder: catalogue 978, research 927, poland-check 409, ideas 321 (overlap counted once in the total) |

**Funnel** (from [longlist.md](../ideas/longlist.md), [shortlist.csv](../ideas/shortlist.csv), [shortlist-notes.md](../ideas/shortlist-notes.md) and the two sections of [rejected.md](../rejected.md)):

| Stage | Count | How counted |
|---|---|---|
| Longlist ideas | 167 | L001–L167 table rows |
| Rejected at T20 | 61 | shortlist-notes.md counts; lines in the T20 section of rejected.md |
| Merged into another idea at T20 | 47 | as above (61 + 47 = 108 lines) |
| **Shortlisted** | **59** | rows in shortlist.csv (167 − 108) |
| **Written up** | **24** | files `ideas/<field>/NNN-*.md` |
| **Rejected at review (T24)** | **7** | 009, 015, 018, 019, 020, 022, 024 |
| **Merged at review (T24)** | **3** | 006 → 001; 007 and 017 → 002 |
| **Write-ups still standing** | **14** | 24 − 10 |
| Shortlisted, never researched beyond the quick score | 35 | 59 − 24 |
| Every rejection or merge, all stages | 118 lines | 108 + 10 in rejected.md |

**Bands in shortlist.csv after the review:** 18 rows `5–15%` and 41 rows `<5%` (counted with `collections.Counter` on `chance_band`; the 41 include 7 rejected and 3 merged). Of the 18 rows at `5–15%`, only one is a reviewed write-up (011). The other 17 are quick scores that never faced the §4 opportunity/risk rule. Read them as probably `<5%`: 23 of the 24 write-ups ended at `<5%`.

**Phase 1 vs Phase 2.** Phase 1 also ended with exactly one `5–15%` idea ([phase1-summary.md](../../reports/phase1-summary.md)). Phase 2 ideas are more LLM-native (L1 is 4 in 11 of the 14 standing write-ups). But they did not score better on Polish demand (L5) or distribution (L8), which is where both phases fail.

## 3. Top 20 after review

**How this table was built.** Rejected and merged rows are excluded. The 14 standing write-ups carry their reviewed (T24) scores. The other 6 rows are the best quick-scored ideas that were never written up (sorted by quick weighted score; the four-way tie at 2.9 was broken by higher L6, then L3, which picks L163). Quick scores fell in almost every write-up, and none of them has faced the §4 rule. They have no write-up file, so the link goes to their Poland-check file.

| # | Idea | Field | Weighted | Band | Status | Note |
|---|---|---|---|---|---|---|
| 1 | [002 Teczka legalizacyjna: MOS case files for agencies](../ideas/employment-migration/002-teczka-legalizacyjna.md) | employment-migration | 3.6 | <5% | reviewed | strongest moat; MOS draft law already lists attachments, so the MVP moves to employer annex, corrections and deadline board |
| 2 | [001 KW + plot risk report](../ideas/property/001-kw-plot-risk-report.md) | property | 3.4 | <5% | reviewed (006 merged in) | free ChatGPT on a real odpis never tried; B2C pays once a decade |
| 3 | [004 Claim-file assistant for kancelarie odszkodowawcze](../ideas/legal-compliance/004-claim-file-assistant.md) | legal-compliance | 3.4 | <5% | reviewed | EvenUp pattern; firm count unknown, RODO art. 9 trust |
| 4 | [012 Kontrola rozliczeń NFZ](../ideas/health-care/012-kontrola-rozliczen-nfz.md) | health-care | 3.3 | <5% | reviewed | deepest moat; needs a pilot clinic's data and NFZ domain help |
| 5 | [011 Broker OWU comparison agent](../ideas/sme-ops/011-broker-owu-comparison.md) | sme-ops | 3.2 | **5–15%** | reviewed | only idea keeping 5–15% (O 19, R 24, no H×H risk) |
| 6 | [005 AI biuro zarządcy](../ideas/property/005-ai-biuro-zarzadcy.md) | property | 3.2 | <5% | reviewed | portal vendors sit on the data; partnership route only |
| 7 | [013 Sworn-translation drafts](../ideas/employment-migration/013-sworn-translation-drafts.md) | employment-migration | 3.2 | <5% | reviewed | cheap to test; translator count unsourced |
| 8 | [016 Asystent klienta biura](../ideas/accounting-tax/016-asystent-klienta-biura.md) | accounting-tax | 3.2 | <5% | reviewed | Comarch ships bank-matching agents; one release from a feature |
| 9 | [003 Karta usług opiekuńczych (bon senioralny)](../ideas/health-care/003-karta-uslug-opiekunczych.md) | health-care | 3.1 | <5% | reviewed | SeniorApp on the gmina side; thin-margin payers |
| 10 | [014 Sekretariat PISP](../ideas/legal-compliance/014-sekretariat-pisp.md) | legal-compliance | 3.1 | <5% | reviewed | Wolters Kluwer holds PISP pickup and Libra AI |
| 11 | [021 School licence for pedagodzy and psycholodzy](../ideas/education/021-school-pedagogue-licence.md) | education | 3.1 | <5% | reviewed | ZPE guide names WOPFU as off-limits for AI |
| 12 | [023 Oferta z maila: RFQ-to-quote for wholesalers](../ideas/sme-ops/023-oferta-z-maila.md) | sme-ops | 3.1 | <5% | reviewed | cleanest gap and best analogue; demand and market size unknown |
| 13 | L088 RCN-based CMA PDF for estate agents ([B/TH57](../poland-check/B/TH57-real-estate-agency-investor-tools.md)) | property | 3.1 | 5–15% (quick) | quick score only | Otodom can add it |
| 14 | [008 Wycena z notatki for installers](../ideas/property/008-wycena-z-notatki.md) | property | 3.0 | <5% | reviewed | two H×H risks; needs a wholesaler or manufacturer partner |
| 15 | [010 Teczka sprzedażowa](../ideas/accounting-tax/010-teczka-sprzedazowa.md) | accounting-tax | 3.0 | <5% | reviewed | one-off purchase; depends on a listing-site partner |
| 16 | L033 Multilingual pre-screening for staffing agencies ([A/TH33](../poland-check/A/TH33-ai-recruiting-interviews-screening.md)) | employment-migration | 3.0 | 5–15% (quick) | quick score only | AI Act hiring line; counsel opinion needed |
| 17 | L106 Physiotherapy scribe with NFZ rehab docs ([A/TH01](../poland-check/A/TH01-ambient-clinical-scribe.md)) | health-care | 3.0 | 5–15% (quick) | quick score only | Heidi and Noa already work in Polish |
| 18 | L046 Citizenship civics + B2 prep ([B/TH39](../poland-check/B/TH39-national-migration-exam-prep.md)) | employment-migration | 3.0 | 5–15% (quick) | quick score only | depends on a draft law |
| 19 | L010 Urzędowa skrzynka biura ([A/TH17](../poland-check/A/TH17-agents-accounting-tax-firms.md)) | accounting-tax | 3.0 | 5–15% (quick) | quick score only | automated ZUS PUE access may breach terms |
| 20 | L163 Polish voicebot QA harness ([A/TH24](../poland-check/A/TH24-local-language-voice-cs-agents.md)) | sme-ops | 2.9 | 5–15% (quick) | quick score only | fails the customer-count sanity check |

## 4. Top 5 for validation

**How they were picked.** Only standing (not rejected, not merged) write-ups were eligible. Within them, the pick favours (a) the reviewed band and score, (b) a moat the review did not break, and (c) a test that settles the riskiest assumption in one week for ≤200 PLN. [012](../ideas/health-care/012-kontrola-rozliczen-nfz.md) scores higher than two of the five, but it cannot be tested without a clinic's data, so it is a wildcard (section 7). [013](../ideas/employment-migration/013-sworn-translation-drafts.md) is the runner-up: its first step costs nothing (count Ukrainian-language entries on the Ministry of Justice list).

All five are B2B and need phone outbound. All five plans are concierge tests: the "product" is done by hand plus an LLM, and nothing is built for production. Prices and go/no-go numbers come from each write-up's own test and kill criteria, adjusted for the T24 review.

### 4.1 [011 Submission and OWU comparison agent for small SME-lines brokers](../ideas/sme-ops/011-broker-owu-comparison.md): weighted 3.2, `5–15%`
- **Why it's here:** the only idea that keeps `5–15%` after review (O 19, R 24, no H×H risk). The gap is clean: no Polish or Western broker-side placement tool was found in two searches. Only ~25 offices at 399 PLN/month are needed.
- **Western analogue and traction:** FurtherAI (US), US$25M Series A led by a16z (2025-10), named carrier and MGA customers; Handle (US/MX), US$6M seed from a16z (2026-03), 75+ active brokers in Mexico; Segura (BR), US$8M seed. All figures are company claims, and there is no retention data ("promising", L2 3).
- **Polish edge:** OWU wording per insurer and per product, compared clause by clause; the IDD needs analysis (APK) under the ustawa o dystrybucji ubezpieczeń; commercial placement by e-mail RFQ to underwriters; line vocabulary (OC przewoźnika CMR vs domestic, franszyza integralna/redukcyjna). The public KNF register gives a complete outbound list.
- **Top 3 opportunities:** a small number of offices is enough for founder-led sales (M×M); the OWU clause library compounds across customers (M×M); OC przewoźnika renewals keep usage steady (M×M).
- **Top 3 risks:** a missed exclusion exposes the broker, so nobody trusts the table (M×H); small brokers place too few commercial policies to justify 399 PLN (M×H); conservative buyers plus 40 h/month make sales slow (H×M). A watch item from the review: insurers (Compensa, PZU) are automating their side of the same inquiry e-mail.
- **Riskiest assumption:** a 1–10 person brokerage places at least 5 commercial policies a month by e-mail RFQ and would trust an AI comparison table enough to pay for it.
- **Validation plan (5 days, ≤100 PLN):**
  1. Day 1: download the current OC przewoźnika OWU of 6 insurers from their websites. With an LLM, build one side-by-side table (sum insured, sub-limits, territorial scope, exclusions, deductibles), every cell citing page and paragraph. Check every cell by hand and record field accuracy.
  2. Day 1: read the KNF 2024 broker report for today's broker count (the write-up still uses the 2017 figure of ~1.5k).
  3. Day 2: take 40 small brokerage firms from the KNF register in Mazowieckie, Wielkopolska and Łódź. Send each a short e-mail with the anonymised sample table: "Want this for your next OC przewoźnika placement? Free for one placement."
  4. Days 3–5: follow up by phone. Ask how many commercial placements they do a month, how long a comparison takes, what software they pay for, and whether 399 PLN/month is acceptable. Run one live placement for free for anyone who sends one.
  - **What to build:** nothing beyond a prompt, a JSON schema for an OWU and a spreadsheet. Cost: LLM API (a few PLN) and an e-mail tool, if you need one.
  - **Go:** ≥3 calls booked from 40 e-mails, **and** ≥2 brokers with ≥5 commercial placements a month, **and** ≥1 sends a live placement, **and** table field accuracy ≥95% after two prompt iterations.
  - **No-go:** <3 calls from 40, or a median <5 placements a month among those called, or accuracy <95% after two iterations.

### 4.2 [002 "Teczka legalizacyjna": MOS case-file agent for agencies and staffing firms](../ideas/employment-migration/002-teczka-legalizacyjna.md): weighted 3.6, `<5%`
- **Why it's here:** the highest reviewed score and the strongest localization moat (L4 5) of the whole set. It absorbed two other write-ups ([007](../ideas/accounting-tax/007-pit-assistant-foreign-employees.md), [017](../ideas/employment-migration/017-mos-bez-stresu.md)) as add-ons. It fell to `<5%` because rules change often (R1 H×H) and the MOS draft law (UD163) already lists mandatory attachments.
- **Western analogue and traction:** US only, all early. Alma (US$17M Series A, round date unverified), CaseBlink (US$2M pre-seed, 2025-03), Visalaw.ai (US$1.6M seed). No revenue or retention data (L2 2).
- **Polish edge:** MOS 2.0 is the only filing channel since 2026-04-27 (no API); the CUKR window runs 2026-05-04 to 2027-03-04; there are 16 voivodeship offices with different practice; employer fines run 3,000–50,000 PLN; ponaglenie under art. 37 KPA. KRAZ lists 8,550 agencies (end-2024) as an outbound list.
- **Top 3 opportunities:** the CUKR wave drives bulk demand from employers (M×H after review); an office-practice tracker that agencies feed becomes a network asset (M×H); fine exposure sells the deadline board to employers' HR (M×M).
- **Top 3 risks:** MOS form and office practice change often, and a stale checklist costs a client's case (H×H); agencies refuse a tool that commoditises their know-how (M×H); the state's own MOS guidance removes the field-sheet value (H×M after review).
- **Riskiest assumption:** staffing firms (not legalisation agencies, who sell the know-how) will pay ~399 PLN/month for an employer annex, corrections workflow and a deadline board.
- **Validation plan (5 days, ≤100 PLN):**
  1. Day 1: download KRAZ and filter to ~100 agencies in mazowieckie and wielkopolskie whose sites mention foreigners or legalizacja. Prefer staffing firms over pure legalisation agencies (T24).
  2. Day 1: make by hand the pieces the state does not cover: an employer annex (Załącznik nr 1) draft from KRS/CEIDG data, and a deadline-board spreadsheet per worker (residence document expiry, notification duties) with an e-mail reminder.
  3. Days 2–3: phone and e-mail the 100: "We'll prepare the employer annex and a deadline board for 5 of your foreign workers, free, within 24 h; then 399 PLN/month." Ask which MOS step hurts most today.
  4. Days 3–5: deliver by hand plus ChatGPT (concierge). Log the minutes each case saves and every MOS change you hit.
  - **What to build:** a spreadsheet template and two prompt templates; a domain and an e-mail tool if needed (~100 PLN).
  - **Go:** ≥5 agencies send real cases **and** ≥2 say yes to 399 PLN/month.
  - **No-go:** <3 of 100 reply, or agencies say it saves <30 minutes per case, or MOS changes break the checklist twice during the week.

### 4.3 [023 "Oferta z maila": RFQ-to-quote and order entry for technical wholesalers](../ideas/sme-ops/023-oferta-z-maila.md): weighted 3.1, `<5%`
- **Why it's here:** the cleanest gap and the best-evidenced Western analogue among the standing ideas (L1 4, L2 4, L3 4). The review called it "the cleanest gap of the batch" and said a positive outreach test would justify a rescore to `5–15%`. General assistants cannot match "YDYp 3x2,5" to a wholesaler's own indeks and price group without the catalogue, which is the strongest defence against absorption in the set.
- **Western analogue and traction:** Parspec (US), US$31.5M raised, 4 of the 5 largest US electrical distributors, 4× revenue in 12 months; Mercura (DE), seed led by TQ Ventures, SignalFire and Y Combinator, profitable from the start, customers in Europe and the US (re-fetched in T24).
- **Polish edge:** connectors for Subiekt nexo/GT and Comarch Optima (InsERT nexo serves "over 300 thousand firms", undated figure), often on-premise; Polish technical shorthand (YDYp, YKY, OMY), local brands, the wholesaler's own indeks vs EAN; the industry structure of family-owned regional wholesalers with installers e-mailing lists and photos.
- **Top 3 opportunities:** only ~20 wholesalers needed, with a visible cost (salespeople at 6–12k PLN gross) (M×M); usage-based pricing grows with volume (M×M); one Subiekt/Optima connector serves many wholesalers (M×M).
- **Top 3 risks:** owners don't see quoting as worth paying for (M×H); wrong matches on technical products produce wrong quotes (M×H); family wholesalers buy slowly and want visits (H×M). Kill signal: any Mercura Polish page or job ad.
- **Riskiest assumption:** a quote takes a salesperson ≥10 minutes today, and an LLM matches Polish technical lines to the wholesaler's indeks with ≥85% accuracy.
- **Validation plan (5–7 days, ≤100 PLN):**
  1. Day 1: list 20 regional electrical and HVAC wholesalers (Google Maps plus CEIDG/KRS by PKD 46.43/46.73/46.74).
  2. Days 1–2: call all 20. Ask how many e-mailed enquiries they get a day, how long a quote takes, and who does it. Ask 5 of them to send 50 anonymised enquiries plus a catalogue export (CSV from Subiekt/Optima).
  3. Days 3–5: build a throwaway Python script: extract lines from PDF/Excel/photo/text into JSON, embed the catalogue, match with a confidence score, output a priced CSV. Hand-label the correct match for each line and measure line accuracy.
  4. Days 6–7: show each wholesaler their matched quotes and ask about a paid pilot at 499 PLN/month plus 1,500 PLN setup.
  - **What to build:** the matching script and a results table only. Tokens ≈ US$0.06 per 50-line enquiry (write-up estimate), so under 50 PLN in total.
  - **Go:** ≥3 wholesalers send samples, **and** line accuracy ≥85%, **and** quotes take ≥10 minutes today, **and** ≥1 asks for a paid pilot.
  - **No-go:** <3 send samples, or accuracy <85%, or quotes take <10 minutes today.

### 4.4 [004 Claim-file assistant for kancelarie odszkodowawcze](../ideas/legal-compliance/004-claim-file-assistant.md): weighted 3.4, `<5%`
- **Why it's here:** the strongest Western pattern among the standing ideas and a real local data layer. The review said "the concierge test with 50 firms is cheap and decisive".
- **Western analogue and traction:** EvenUp (US), US$150M Series E at >US$2B (2025-10), 2,000+ firms, ARR doubled y/y (company claim); Supio (US), US$60M Series B (2025-04), 4× ARR since Series A. The spread widened in review to insurer-side tools in CA and the UK.
- **Polish edge:** zadośćuczynienie is set by courts from case practice (art. 445/446 KC), not from medical bills, so EvenUp's core does not transfer. Instead: an amount corpus from SAOS judgments; the FKZM patient-compensation route (1,574 applications in 2024); Polish medical records and vocabulary.
- **Top 3 opportunities:** the SAOS amount corpus becomes an asset firms and adjusters want (M×H); the FKZM route grows (M×M); post-CHF firms move staff to injury claims (M×M).
- **Top 3 risks:** firms already paste files into ChatGPT and see little extra value (H×M); a small, price-sensitive market (M×H); firms won't upload art. 9 medical data to a one-person vendor (M×H).
- **Riskiest assumption:** the SAOS-backed amount range adds enough over a free Claude/Gemini chronology that a firm will pay ≥300 PLN/month, and enough firms exist (the §3 sanity check needs ~400 reachable firms, and the count is unknown).
- **Validation plan (5 days, ≤100 PLN):**
  1. Day 1: list ~100 firms from the "kancelaria odszkodowawcza [miasto]" results in 8 cities. This list doubles as the first market-size count.
  2. Day 1: in SAOS, search art. 445 KC judgments for 3 common injury types and note awarded amounts for 10 judgments each (by hand).
  3. Day 2: e-mail 50 firms: "Send one anonymised injury file; within 24 h you get a dated chronology plus 5 similar SAOS judgments with amounts, free."
  4. Days 3–5: deliver by hand plus an LLM, then ask a price question by phone: would they pay 499 PLN/month for up to 20 files?
  - **What to build:** a chronology prompt and a spreadsheet of SAOS amounts. Use only anonymised files, and say so in the e-mail.
  - **Go:** ≥5 of 50 send a file, **and** ≥1 would pay ≥300 PLN/month after seeing the output, **and** the firm list reaches ≥400 (or a source shows it).
  - **No-go:** <5 of 50 send a file, or nobody would pay ≥300 PLN/month, or ≥3 refuse because of medical-data hosting.

### 4.5 [001 "Czy ta księga jest czysta?" KW + plot risk report](../ideas/property/001-kw-plot-risk-report.md): weighted 3.4, `<5%`
- **Why it's here:** a strong Western analogue, near-zero token cost (gross margin >95% at 69 PLN), very testable output, and a decisive first step that costs nothing: does free ChatGPT already find the same risks on a real odpis? It absorbed [006](../ideas/property/006-czy-tu-zbuduje.md) as a plot add-on.
- **Western analogue and traction:** Orbital (UK), US$60M Series B (2026-01), 5,000+ professionals and 250,000+ transactions a year. The analogue is B2B law-firm use. The B2C form exists only as a free state service in Gyeonggi (KR), which supports the "free beats 69 PLN" risk.
- **Polish edge:** księgi wieczyste structure (działy I–IV, wzmianki, hipoteka przymusowa, służebność przesyłu), the cross-check of the flat, building and land KW, the parcel check via ULDK/EGiB, and Polish notarial practice. After review the moat is "weeks to learn", not months (L4 5 → 4).
- **Top 3 opportunities:** agents and brokers buy it as a sales tool (M×H); a combined plot-buyer product with 006 (H×M, but this is a build choice, not market evidence); the mortgage revival lifts transaction volume (M×M).
- **Top 3 risks:** buyers see notary and bank checks as enough, so B2C willingness to pay is near zero (H×H); ChatGPT/Gemini "read this odpis" is good enough (M×H); one purchase per decade, no retention (H×M). A review point: agents may not want buyers to get a risk list about their own listing.
- **Riskiest assumption:** the report finds risks a free assistant misses, and someone (buyer or agent) pays for that difference.
- **Validation plan (7 days, ≤200 PLN):**
  1. Days 1–2 (free): collect 20 real odpisy (your own, friends', or KW numbers published in listings; EKW viewing by number is CAPTCHA-gated, so do it by hand; check that viewing is free before relying on it, unverified here). Paste each into free ChatGPT, then run the planned prompt plus a ULDK parcel-area check. Count the risks each finds.
  2. Stop here if free ChatGPT finds the same risks in ≥18 of 20.
  3. Days 3–4: a one-page landing page, "Wgraj odpis księgi wieczystej, w 10 minut dostaniesz listę ryzyk — 69 PLN", with a pre-order button (payment link if you have a gateway; otherwise "reserve, pay on delivery", which is a weaker signal). 150 PLN of Google Ads on "sprawdzenie księgi wieczystej mieszkania".
  4. Days 3–7: e-mail or phone 10 estate agencies and 5 mortgage brokers in one city and offer 3 free reports on listings they have.
  - **What to build:** the landing page and a manual report template; nothing automated.
  - **Go:** the MVP prompt finds material risks ChatGPT misses in ≥3 of 20 odpisy, **and** (≥5 pre-orders **or** ≥3 agencies ask for a price).
  - **No-go:** ChatGPT matches in ≥18 of 20, or <2 pre-orders from ~300 ad clicks and no agency interested after 3 free reports each. (Whether 150 PLN buys ~300 clicks is unverified; judge on the conversion rate if clicks are fewer.)

### 4.6 Order and decision rule
- **Order:** week 1 → 011 (the only `5–15%` idea; ≤100 PLN). Week 2 → 023 (needs samples and a script, so start the calls early). Week 3 → 002. Week 4 → 004. Day 1 of 001 (the ChatGPT comparison) costs nothing and can run in any spare evening; its ad test goes last, in week 5. Total spend at most ~600 PLN over five weeks (each plan's cap), probably less, so about one month's budget.
- **Decision rule:** an idea that passes every Go condition gets rescored with the new evidence. If L5 and L8 reach 4 with sources, it moves to `5–15%` or above, and it gets a 6-week MVP. If two pass, pick the one with more paying-intent answers, not the higher score. If none pass, do not open a new desk-research round. See section 9.

## 5. Demographic opportunity map
Which Polish demand drivers ([demography.md](../research/poland/demography.md#demand-drivers)) have no good product yet, judged by the Poland checks and the reviewed ideas. "No good product" means no Polish or Western product does the job well in Poland **and** no idea in this research survived review with a viable payer.

| Driver | What the research found | Ideas (status) | Verdict |
|---|---|---|---|
| DD1 Ageing faster than care capacity | Family care coordination and senior check-in calls have no Polish product, but also no durable Western analogue and weak payers | L120, L122 (quick `<5%`) | **unserved, no payer found** |
| DD2 Bon senioralny (new public buyer of care hours) | Provider-side settlement is open; SeniorApp covers the gmina side | [003](../ideas/health-care/003-karta-uslug-opiekunczych.md) (`<5%`) | partly served; a module for platforms, not a business |
| DD3 Health-system queues | Booking voice agents taken (Docplanner Noa, state CeZ voicebot); NFZ settlement checks open but need domain access | [012](../ideas/health-care/012-kontrola-rozliczen-nfz.md) (`<5%`), [020](../ideas/health-care/020-clinic-phone-agent.md) rejected | open only for someone with NFZ settlement know-how |
| DD4 Mental-health demand | Therapist admin hits the MDR and art. 9 line; scribes are taken | L107, L114 rejected (T20) | **unserved, blocked by the founder's no-medical rule** |
| DD5 Shrinking pensions | Pension-gap explainers sit on a financial-advice line; no payer for education alone | L021 rejected (T20) | **unserved, licence-blocked** |
| DD6 ~2 million foreigners settling | The richest driver: legalisation case files, sworn translations, PIT, MOS help. B2C help is free (state, NGOs) or already sold (WoBorders, Mova, PolskiTest) | [002](../ideas/employment-migration/002-teczka-legalizacyjna.md), [013](../ideas/employment-migration/013-sworn-translation-drafts.md) standing; [007](../ideas/accounting-tax/007-pit-assistant-foreign-employees.md), [017](../ideas/employment-migration/017-mos-bez-stresu.md) merged; [018](../ideas/accounting-tax/018-biuro-dla-obcokrajowcow.md), [022](../ideas/employment-migration/022-b1-bez-stresu.md) rejected | **B2B case-file side unserved**; B2C side served or free |
| DD7 Scarce, expensive labour | Back-office hours in small regulated firms: brokers, wholesalers, claims firms, accounting offices, installers, property managers. Ledger and suite vendors are adding agents fast | [011](../ideas/sme-ops/011-broker-owu-comparison.md), [023](../ideas/sme-ops/023-oferta-z-maila.md), [004](../ideas/legal-compliance/004-claim-file-assistant.md), [016](../ideas/accounting-tax/016-asystent-klienta-biura.md), [005](../ideas/property/005-ai-biuro-zarzadcy.md), [008](../ideas/property/008-wycena-z-notatki.md) | **unserved in niches without a dominant software vendor** (brokers, wholesalers on Subiekt/Optima) |
| DD8 People living alone | General assistants in Polish cover household admin | L167 rejected (T20) | served by generic tools |
| DD9 Suburbanisation | Plot buildability is mostly free (e-mapa.net, OnGeo); trades quoting is open but needs a channel partner | [006](../ideas/property/006-czy-tu-zbuduje.md) merged, [008](../ideas/property/008-wycena-z-notatki.md) (`<5%`) | partly served |
| DD10 Housing and mortgages revive | KW interpretation has no AI product, but buyers search for access, not interpretation | [001](../ideas/property/001-kw-plot-risk-report.md), [005](../ideas/property/005-ai-biuro-zarzadcy.md) (`<5%`) | gap exists, payer unproven |
| DD11 Education reform, diverse classrooms | Teacher paperwork: the ministry's ZPE guide forbids AI for key opinions; curriculum materials absorbed by ChatGPT and publishers | [015](../ideas/education/015-opinia-i-sprawozdanie.md) rejected, [021](../ideas/education/021-school-pedagogue-licence.md) (`<5%`) | **blocked by guidance**, slow school buying |
| DD12 Rising incomes | A supporting driver for willingness to pay, not a market by itself | — | — |

**Reading.** The clearest unserved demand is B2B work created by DD6 (foreigners' legal stay) and DD7 (labour scarcity in small regulated offices). The drivers with the biggest social weight (DD1 ageing, DD4 mental health, DD5 pensions) stay unserved, but for reasons a solo founder can't fix: no payer, the medical-device line, or the financial-advice line.

## 6. Patterns

**Regions.** Counted from the "Western analogues" sections of the 14 standing write-ups: R1 North America supplied an analogue for 13 of them (all but 014), R3 DACH & Benelux for 7, R2 UK & Ireland for 2 (001, 003), R9 Gulf & Turkey for 2 (004 TR, 021 SA), and R4 (016 DK), R5 (012 FR), R7 (003 JP), R8 (003 AU) and R10 (011 MX/BR/UY) for 1 each; R6 CEE peers gave 1 adjacent case (023: Duvo, Definic). CEE mainly produced **entry warnings**: 9 CEE products already in Poland and 3 announced (R6 scan, T10). East Asia and the Gulf produced patterns (national tax refund finders, teacher-paperwork apps) but no idea that survived. The US remains the best source of B2B patterns. Germany is the best source of "SME back office on a national system" patterns (plancraft, JUPUS, Mercura), and those are the closest to Polish conditions.

**Themes.** The ideas that survived review are all **back-office agents for small, regulated professional firms** that work on documents the state does not handle: insurance brokers (TH55), legalisation and staffing agencies (TH12), claims firms (TH11), wholesalers (TH61), accounting offices (TH17). 6 of the 7 B2C write-ups (006, 007, 009, 015, 017, 022) were rejected or merged; the seventh, 001, survives only on its B2B tier. The top-ranked global themes (TH16 AI accountant, TH07 legal research, TH01 clinical scribe) were all "taken" or "partial" in Poland: high global spread means the incumbents noticed too.

**Moats.** Two kinds of moat behaved very differently:
- **Moats inside a free state system** (MOS 2.0, EKW/mObywatel, Geoportal/e-mapa, Twój e-PIT, NFZ Terminy, the ZPE guidance) look deep, but the state is also the strongest competitor. It ships the feature for free, or forbids the use case. It hurt 002, 006, 007, 015, 017, 020 and 021 in review.
- **Moats inside a private document flow** (insurers' OWU, a wholesaler's catalogue and price groups, claim files plus SAOS) held up better. The two cleanest gaps (011, 023) are both of this kind.

**What killed ideas in review** (from the reasons in rejected.md and the Review changes lines): a Polish incumbent or platform owner shipping the feature (Comarch: 016, 019; Wolters Kluwer: 014; Docplanner: 020; Allegro/Senvio: 024; Mova/PolskiTest: 022; WoBorders: 018; DocuGov/LEX AI: 009); free state help (006, 007, 015, 017); one-off revenue (007, 009, 010, 022).

## 7. Wildcards (high risk, high upside)
- [012 Kontrola rozliczeń NFZ](../ideas/health-care/012-kontrola-rozliczen-nfz.md): the deepest moat (L4 5; NFZ zarządzenia, SWIAD, ICD-9 PL), money visibly at stake (NFZ degression on over-contract imaging and endoscopy from 2026-04-01), and an analogue with a 2026 Series A (Parallel, FR). It only works with a pilot clinic's data and NFZ settlement know-how, so pursue it only if someone in your network offers both. The suggested wedge is ASDK imaging/endoscopy limit tracking.
- [013 Sworn-translation drafts](../ideas/employment-migration/013-sworn-translation-drafts.md): tiny, cheap and testable, with a public buyer list. The first check (are there ≥1,000 Ukrainian-language sworn translators on the Ministry of Justice list?) costs nothing and decides most of it. The upside is limited by market size, but the downside is one free afternoon.
- [010 Teczka sprzedażowa](../ideas/accounting-tax/010-teczka-sprzedazowa.md): a demographic wave (up to 80,000 successions by 2030, from older surveys) and no Polish AI sale-pack product. It stands or falls on a listing-site partnership (BizShop, sprzedambiznes.pl) that doesn't exist yet. A pitch to both costs nothing.
- [003 Karta usług opiekuńczych](../ideas/health-care/003-karta-uslug-opiekunczych.md) as a **module sold to SeniorApp-type platforms or large care agencies**, not as a standalone app: a dated public-money driver (bon senioralny, 2026–2028), but thin-margin payers.
- L046 Citizenship civics + B2 prep ([B/TH39](../poland-check/B/TH39-national-migration-exam-prep.md), quick score only): first mover on the day an MSWiA amendment passes, if it passes. Watch the law, don't build.

## 8. What the research covered poorly
- **No hands-on trial of a Western leader.** The brief's first check ("actually try the Western leader") was almost never done: leaders were demo-led and no accounts were created. `works_in_polish` is `unknown` for 79% of catalogue rows.
- **No test of free general assistants on real Polish documents.** This is the main absorption risk for 001, 004, 011 and 013, and it was argued, not measured.
- **Demand evidence is indirect.** It comes from Google autocomplete, job ads and press. No interviews or calls were made, and Google Trends, Keyword Planner, Facebook groups and Wykop were not checked (they need a login or JavaScript).
- **Market sizes are missing** for most standing B2B ideas: brokers (2017 figure only), claims firms (unknown), technical wholesalers (unknown), Ukrainian-language sworn translators (unknown). So the §3 customer-count sanity check could not be passed for 004, 013 or 023.
- **Retention data is almost absent** from the catalogue, so "durable" in THEMES.md is a relative label, and L2 never had NRR or churn behind it.
- **Many facts come from search excerpts** rather than fetched pages (marked in each file). 11 countries are thin (<5 products), and Google Play charts and accelerator portfolios were not screened in most regions.
- **B2C was explored less** and scored worse. The founder profile (40 h/month, 500 PLN budget) pushes toward B2B outbound, and that is what survived.

## 9. Open questions for you
1. **Network access.** Do you know anyone among insurance brokers, staffing or legalisation agencies, compensation-claims firms, technical wholesalers, or clinics with an NFZ contract? One warm introduction changes L8 more than any desk research, and it is the only way 012 becomes testable.
2. **Phone outbound.** All five tests need 20–100 calls or e-mails in a week. Is that acceptable inside your 40 h/month, or should the plans be reshaped toward e-mail and landing pages only (slower and weaker signals)?
3. **The success bar.** With "10,000 PLN MRR within 12 months" nothing clears `5–15%` except 011. Would a smaller first goal (for example 3–5k PLN MRR as a side business) be acceptable? It would favour cheap, small-market ideas such as 013 and 001.
4. **Partners and revenue share.** Would you build with a domain partner (an NFZ settlement specialist for 012, a broker for 011) for equity or a revenue share?
5. **Medical and personal data.** 004 and 012 need art. 9 health data handled with EU hosting, DPAs and deletion policies. Are you willing to carry that compliance work as a solo founder?
6. **What next if all five tests fail.** The recommendation is a Phase 3 of primary research: 30 short interviews across the 3–4 professional niches that kept appearing (brokers, staffing agencies, wholesalers, accounting offices) to find a pain they already pay for, rather than another scan of foreign products. Do you agree?
