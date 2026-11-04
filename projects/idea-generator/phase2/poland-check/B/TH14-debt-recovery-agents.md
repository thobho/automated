# TH14 — Debt recovery agents (Poland check)

Theme: [THEMES.md#th14](../../themes/THEMES.md#th14) · rank 26, batch B · sources accessed **2026-11-04** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Vindicat.pl | Self-service online collection: import invoices, "robot" sends reminders, generates wezwania, EPU e-court claims, settlements, debt exchange; in-house law firm; wFirma integration; no AI claimed | **8% success fee** on recovered amount; subscription and law-firm prices on separate pages | **20,000+ companies**; claims 93% settled amicably | [vindicat.pl](https://vindicat.pl/) |
| Invoicing/ERP modules (Fakturownia, wFirma "miękka windykacja", Fakturowo, Comarch Optima "Windykacja należności") | Automatic e-mail/SMS payment reminders inside the invoicing tool | included in plans | hundreds of thousands of SMEs (invoicing user bases) | [wFirma help](https://pomoc.wfirma.pl/temat/miekka-windykacja); [Comarch Optima docs](https://pomoc.comarch.pl/optima/pl/2025/dokumentacja/windykacja-naleznosci-2/); [Fakturowo blog](https://www.fakturowo.pl/blog/nowoczesne-metody-windykacji) |
| TSL specialists (Transcash, Transinkasso and similar) | Collection for carriers, incl. German debtors, success fee | success fee (rates not found) | road carriers | [trans.info on Transcash](https://trans.info/pl/platnicy-z-niemiec-na-radarze-transcash-285535) |
| PAIR Finance (DE, AI collection) | AI-driven B2C receivables management; Polish-language site, Poland listed among 13 markets | enterprise | Klarna, Douglas, AUTODOC (no Polish client named) | [pairfinance.com/pl](https://pairfinance.com/pl/success-stories) |
| Ainora (LT) | Voice AI payment reminders, marketed in Polish (2026-06 blog) | not found | not found | [ainora.lt PL blog](https://ainora.lt/pl/blog/windykacja-ai-przypomnienia-o-platnosciach-glosowe-2026) |

Plus the classic collection industry (KRD, Kaczmarski, Kruk, BEST) for B2C portfolios and B2B inkaso.

## 2. Does the Western leader already serve Poland?
- **Garfield.Law** (UK): SRA-regulated AI law firm for claims up to £10,000, £2 per chaser, £7.50 per letter before action, English small-claims court; UK accounting integrations only. **Not in PL** ([garfield.law](https://www.garfield.law/)).
- **PAIR Finance** (DE) **is in PL** with a Polish site (enterprise B2C portfolios).
- **QuickLegal** (RO) is Romanian-law only; **Mozart** (UY), **CollectWise**, **Domu** (US) are home-market.
- Could not check: PAIR Finance's Polish client list or pricing (demo-led).

## 3. Polish demand signals
- Autocomplete (2026-11-04): "windykacja faktur" → 10 incl. "po jakim czasie", "z niemiec", "**transportowych**", "**zagranicznych**", "koszt", "fakturownia windykacja"; "wezwanie do zapłaty wzór" → 10 (pdf, doc, word, darmowy, krd); "nakaz zapłaty e-sąd" → 7 incl. "co dalej forum" (mostly debtors); "windykacja transport" → 4; "windykacja ai" → only firm names.
- Press: carriers are not paid on time for close to 40% of receivables ([Forsal](https://forsal.pl/artykuly/651241,przewoznicy-przygnieceni-platniczymi-zatorami-windykatorzy-walcza-o-ich-dlugi.html)); a typical cross-border transport claim is 500–3,000 EUR and the process often costs about as much as the claim ([trans.info](https://trans.info/pl/odzyskiwanie-naleznosci-od-zagranicznych-kontrahentow-co-daje-przewoznikom-prawo-unijne-488545)).

## 4. What adaptation needs
EPU e-sąd (Sąd Rejonowy Lublin-Zachód), ustawa o przeciwdziałaniu nadmiernym opóźnieniom (40/70/100 EUR rekompensata, interest), KRD/BIG registries, M12 KRZ for insolvent debtors, M04 biała lista and M09/M10 KRS/CEIDG debtor checks, M01 KSeF (from 2026 the invoice and its KSeF number are a clean evidence trail), M46 Fakturownia/inFakt/wFirma APIs, UOKiK rules for consumer collection. Cross-border: EU payment order (EPU-UE), German Mahnverfahren.

## 5. Demographic or social driver
No strong demographic driver. DD7 labour costs push small firms to automate back office; KSeF (dated trigger 2026) makes overdue-invoice data machine-readable.

## 6. CEE check
QuickLegal (RO) does AI-assisted SME invoice recovery under Romanian law ([R6 catalogue](../../catalogue/R6-cee-peers.csv) `R6-RO-004`); no sign of PL entry.

## 7. Verdict: **taken**
Self-service SME collection with document generation and EPU filing is already sold in Poland at 8% success fee to 20,000+ firms (Vindicat), reminders are built into every invoicing tool, PAIR Finance covers enterprise B2C in Polish, and TSL has specialist collectors. An LLM layer (reading debtor replies, negotiating instalments) is an incremental feature for incumbents rather than a new product.

**Seed idea (residue, weak):** cross-border claim pack for Polish carriers: from the CMR, zlecenie and KSeF invoice, the tool drafts the German/French demand with the 40 EUR rekompensata and statutory interest, then the EU payment order, for a flat fee per claim; crowded by TSL collectors.
