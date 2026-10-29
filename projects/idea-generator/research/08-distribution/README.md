# Lens 8 — Cheap distribution

Research for lens 8 of [BRIEF.md](../../BRIEF.md); scoring anchors in [method/criteria.md](../../method/criteria.md). All sources accessed 2026-10-29 (today). IDs `L8-Fnn` are stable anchors. The question: **is there a concrete route to the first 100 customers on about 40 hours of non-code work and PLN 500 a month?** Most pages were read through a summarising fetch tool and several were search summaries only; each finding says which.

**Headline:** 25 findings (F01–F25) in three topic files; Poland, Germany, USA/global platforms. Patterns:
1. **No platform hands out customers; directories help only after you have references.** Allegro's only third-party showcase is a list of 12 certified integrators, all incumbents (F01, F02); DATEV-Marktplatz requires a DATEV Online API integration, reference customers and a financial check, and had 2,133 monthly active users (F06); Shopify ranking and "Built for Shopify" depend on installs and reviews you do not have yet (F03). Atlassian's 0% fee on Forge up to USD 1M (F05) and WordPress.org / Chrome (F04, F07) are open but need a product that earns discovery by search.
2. **Accounting offices are a channel that already has a price.** ifirma pays PLN 10–100 per referral (F08), wFirma pays implementation partners 30% of net package price and recommends PLN 350/hour for services (F09). Offices are used to recurring vendor commission, so a tool that sells through them should plan a rev-share, and a tool they can resell neutrally across programmes is a gap.
3. **Cold e-mail is the legally weakest route in both countries.** Poland: PKE art. 398 needs prior consent and covers companies (F13); Germany: § 7 UWG needs prior express consent for e-mail (F14); GDPR legitimate-interest arguments are contested (F15). The lists exist for free (CEIDG warehouse, REGON API, KIDP lookup; F10–F12) but contacting from them is risky. Plan for inbound and consented channels.
4. **SEO has a real but narrow gap in Polish "free/no login" KSeF phrases** (F16–F17), while German E-Rechnung validator/viewer phrases are already served by free state tools (F18).
5. **Paid ads are a test tool, not a channel.** The only Polish-specific CPC claim (EUR 0.17) has no method (F21); B2B benchmarks of USD 5–14 per click (F21, F22) make PLN 500/month about 10–40 LinkedIn clicks or 100–250 Google clicks (my estimate).
6. **Founder stories say audience or insider status comes first** (F23, F24); the sources are self-reported or vendor blogs, and I found no Polish first-100 story (Gaps).

## Topic files
| File | Findings |
|---|---|
| [marketplaces-and-directories.md](marketplaces-and-directories.md) | F01 Allegro Certyfikowany Integrator, F02 the 12 listed integrators, F03 Shopify ranking and BFS, F04 WordPress.org freemium rules, F05 Atlassian fees, F06 DATEV-Marktplatz, F07 Chrome Web Store fee |
| [partners-lists-and-law.md](partners-lists-and-law.md) | F08 ifirma partner programme, F09 wFirma partner programmes, F10 CEIDG warehouse, F11 REGON BIR, F12 KIDP / KIBR / SKwP, F13 PKE art. 398, F14 UWG § 7, F15 GDPR on cold e-mail |
| [search-communities-ads-and-stories.md](search-communities-ads-and-stories.md) | F16 KSeF autocomplete, F17 free official KSeF tools, F18 German E-Rechnung autocomplete, F19 Wykop #ksef, F20 accountants' hangouts, F21 Google Ads cost, F22 LinkedIn Ads cost, F23 FeedbackPanda, F24 founder stories, F25 Shopify first-100 guides |

## Distribution readings of recurring themes (my judgement, not scores)
Indicative L8 cap per theme (criteria.md: 5 = a concrete channel reaching 100 customers with under PLN 500/month and under 10 h/month). T12 must score concrete ideas.

| Theme | Best route found | Indicative L8 cap | Findings |
|---|---|---|---|
| KSeF receive-side tools for micro-firms | Free no-login viewer/downloader as SEO + Wykop; paid plan for notifications/archive | 3–4 | F16, F17, F19 |
| KSeF tools for accounting offices | Partner/rev-share with offices; neutral across accounting programmes; no list-based cold e-mail | 3 | F08, F09, F13 |
| Allegro / BaseLinker seller tools | Own SEO + BaseLinker/Allegro communities; certification only after traction | 2–3 | F01, F02 |
| Shopify apps | Search terms in the store + outreach to people who opt in; slow start without reviews | 2–3 | F03, F25 |
| WordPress / Chrome utilities | Free listing, organic discovery; works only if a searchable need exists | 3 | F04, F07 |
| Atlassian apps | Open marketplace, 0% fee to USD 1M; B2B English buyers, no Polish moat | 3 | F05 |
| German E-Rechnung tools | DATEV-Marktplatz is gated; SEO crowded by free validators; cold mail illegal without consent | 2 | F06, F14, F18 |
| Salon / booking | Not researched beyond the legal rules (no directory evidence found) | 2 (unverified) | F13 |
| NIS2 / CRA compliance | Autocomplete shows almost no Polish long tail for NIS2 phrases (0–1 suggestions); English CRA phrases exist | 2 (unverified) | Coverage |

## Seeds
Idea sketches inspired by findings; none validated. Each states the distribution route only; price, competition and feasibility come from other lenses.
1. **"Podgląd KSeF" free no-login viewer plus paid watcher.** Browser-side XML/QR to readable invoice and PDF, targeting phrases like "ksef podgląd faktury bez logowania"; upsell: new-invoice notifications and archive. Route: SEO + Wykop + a free tool people opt into. [L8-F16](search-communities-ads-and-stories.md), [L8-F17](search-communities-ads-and-stories.md), [L8-F19](search-communities-ads-and-stories.md). Overlaps lens 6/7 seeds on receive-side KSeF inbox.
2. **Accounting-office KSeF dashboard sold with a recurring rev-share.** One screen for an office across clients' incoming invoices; offices resell with 20–30% recurring commission modelled on wFirma's 30%. [L8-F09](partners-lists-and-law.md), [L8-F08](partners-lists-and-law.md).
3. **Neutral connector for offices that use several accounting programmes.** Offices are bound to each vendor's programme (wFirma § 9 asks partners not to push competitors); a vendor-neutral tool is an angle. [L8-F09](partners-lists-and-law.md).
4. **Consent-first outbound to tax advisers.** A free KSeF checklist or webinar for tax advisers collected via public KIDP-linked channels, building a list of people who opted in, instead of cold mail. [L8-F12](partners-lists-and-law.md), [L8-F13](partners-lists-and-law.md).
5. **Atlassian Forge app for a Polish/EU compliance niche.** 0% fee up to USD 1M; the open question is whether a Polish moat exists on an English marketplace. [L8-F05](marketplaces-and-directories.md).
6. **WordPress plugin front door + SaaS back end for an e-invoicing or compliance task** (the SaaS does real work, per the guideline on SaaS plugins). [L8-F04](marketplaces-and-directories.md).
7. **Allegro-side add-on that sits on BaseLinker's API instead of competing with the 12 certified integrators.** Route: BaseLinker users' communities and own SEO; certification as month-6 credibility. [L8-F01](marketplaces-and-directories.md), [L8-F02](marketplaces-and-directories.md).
8. **E-Rechnung hand-off to DATEV for small German firms, validated through content, not mail.** Only after a reference customer; DATEV listing is a later gate. [L8-F06](marketplaces-and-directories.md), [L8-F18](search-communities-ads-and-stories.md).
9. **"Insider co-founder" screen for the niche choice.** Not a product: pick the niche where the founder has a personal route in (relative who owns an office or salon), the pattern behind FeedbackPanda. [L8-F23](search-communities-ads-and-stories.md), [L8-F24](search-communities-ads-and-stories.md).

## Coverage
- **Sources read in full or in the relevant part (fetch tool, summarised):** 27 pages — Allegro Developer announcement and Certified Integrators page, Shopify BFS docs, WordPress plugin guidelines, Atlassian developer page and revenue-share thread, DATEV-Marktplatz FAQ, Chrome Web Store registration page, ifirma and wFirma partner pages (3), CEIDG warehouse page, REGON BIR page, KIDP home, gesetze-im-internet.de UWG § 7, standardyprawa.pl PKE art. 398, poradnikprzedsiebiorcy.pl cold-mailing article, Wykop #ksef, Norman KSeF guide, landingi, codedesign, seo-day, StoreCensus, Draper, theygotacquired, elixirforum.
- **Search summaries only (not opened):** about 12 pages cited as such (e.g. ifirma/Sejm consent commentary, IHK Cologne/Munich, KPMG, Woodpecker, kluczesoft, PARP, Shopify community reply).
- **Machine queries:** 22 Google autocomplete stems (17 Polish, 5 German) — see F16, F18.
- **Searches run:** about 27 (English, Polish, German).
- **Countries:** Poland (most), Germany, USA/global platforms (Atlassian, Shopify, Chrome, WordPress). No other EU market covered.
- **Found nothing or blocked:** Allegro app directory (none exists, F01); Polish Google CPC with method; BaseLinker partner/extension programme (search found none); Symfonia partner page (404); InsERT/Comarch ISV programmes; Facebook group names and sizes; GOFIN stats (403); SKwP total members (only a search-summary claim of branch counts, not verified, so omitted); count of accounting offices in Poland (GUS PKD 69.20.Z not found); Polish solo-founder first-100 stories; Indie Hackers posts (403); Wolters Kluwer article (403); LinkedIn minimum budget (404); Chrome fee amount on the official page.
- **Reliability notes:** Vendor blogs (Norman, StoreCensus, Draper, kluczesoft, landingi, Woodpecker) are interested sources and flagged. No text aimed at AI assistants was observed in the pages read.

## Gaps
1. **Polish keyword volumes and difficulty** for the F16 phrases: use Google Keyword Planner (free account) and Ahrefs/Senuto free tools; check page one for each. Also test NIS2/CRA phrases properly (only autocomplete done).
2. **Real CPC in Poland** for "program do ksef", "ksef faktury": Keyword Planner, then a PLN 100 test.
3. **Facebook / GOFIN / Wykop community sizes and self-promotion rules**: join and read rules; a manual step for T-validation.
4. **Legal opinion** on cold e-mail to companies and on LinkedIn messages under PKE art. 398 / UŚUDE / GDPR art. 14, with UODO and UKE guidance (not found); ask a Polish privacy lawyer or read UODO's published decisions.
5. **Whether CEIDG data includes e-mail and whether it may be used for marketing**: read the API documentation after Profil Zaufany login and the data-use terms.
6. **Programme terms not read:** Allegro certification regulations, Shopify BFS numeric thresholds, DATEV fee amounts, wFirma add-on commission percentage, inFakt/Fakturownia/Firmao partner terms, Comarch/InsERT/Symfonia ISV programmes.
7. **Current counts**: tax advisers (KIDP; only 2020 found), accounting offices in Poland, salons (CEIDG PKD 96.02.Z), BaseLinker users (a search snippet mentioned "16,000 sellers", unverified).
8. **Salon/booking distribution**: directories (Booksy, Znany Lekarz style marketplaces), Polish beauty communities and industry associations were not researched.
9. **Polish and German solo-founder first-100 stories with primary sources**: try Polish podcasts and bootstrap blogs, Indie Hackers via a browser.
10. **Product Hunt / Hacker News / Reddit launches** as one-day channels for developer tools (lens 8 brief mentions dev tools/APIs; not researched here).
