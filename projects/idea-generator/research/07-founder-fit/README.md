# Lens 7 — Founder fit and feasibility

Research for lens 7 of [BRIEF.md](../../BRIEF.md); scoring anchors in [method/criteria.md](../../method/criteria.md) (5 = MVP in ≤6 weeks on the founder's stack, easy to test automatically, public or self-serve APIs only, little support, no regulatory exposure beyond normal GDPR). All sources accessed 2026-10-29 (today). IDs `L7-Fnn` are stable anchors. This lens asks: **can a solo Polish developer with AI agents ship this within six weeks, without a licence, partner approval or heavy on-call?** It works on gates (who must say yes), licences, building blocks, running costs and maintenance, and applies them to the recurring themes of lenses 1–6.

**Headline:** 28 findings (F01–F28) in four topic files; Poland, Germany/EU, USA/global platforms. Patterns:
1. **The gate is usually the platform, not the code.** Allegro reviews each API application and may refuse without reason (F01); Shopify public-app review ran 3–6 weeks in spring 2026 (F15); Google Play wants 12 testers for 14 days (F06); Apple rejects thin web wrappers (F17). Only KSeF (F02), BaseLinker (F16) and Chrome/WordPress (F07, F08) are self-serve or predictable. A product whose first customer depends on a store listing cannot be promised inside six weeks.
2. **KSeF is feasible but not trivial.** No certification, official OpenAPI and Java/C# clients, free test and demo environments (F02, F22); but rate limits as low as 20 requests/hour for some calls (F03), offline modes for issuing (F19) and repeated API churn (F20). **Receive-side products (fetch, archive, notify, match) are much cheaper to build and support than issue-side products.**
3. **The licence line is easy to cross by accident.** Moving or holding other people's money needs KNF authorisation with EUR 20,000–125,000 initial capital for the licence route (F09); bank-account reading is a registered service (F11, details unverified); individual tax advice is a reserved profession (F14). Document formatting, validation and transport do not touch any of these. Stripe Connect is available in Poland (F10), but its legal effect on the platform is unverified.
4. **Building blocks exist for e-invoicing and booking** (Mustang, KoSIT validator, phive, KSeF clients; F21–F23) - which shortens the build and also lowers the barrier for rivals. Evidence that AI agents make a solo developer reliably faster is weak (F24), and public build-time stories are self-reported (F25): plan scope, not hype.
5. **Money costs are small:** LLM calls cost about USD 0.001–0.02 per document (F26–F27, estimate); selling across the EU through a merchant of record costs 5% + USD 0.50 (F18). The binding costs are founder time and risk, not cash.

## Topic files
| File | Findings |
|---|---|
| [api-access.md](api-access.md) | F01 Allegro API terms, F02 KSeF API access, F03 KSeF rate limits, F04 Peppol Access Point fees, F05 Shopify rules and revenue share, F06 Google Play 12-tester rule, F07 Chrome Web Store, F08 WordPress.org, F15 Shopify review backlog, F17 Apple guidelines |
| [licensing-and-regulation.md](licensing-and-regulation.md) | F09 KNF payment institutions, F10 Stripe Connect, F11 account-information services, F12 AI Act Article 50, F13 medical-device boundary, F14 tax-advice boundary, F28 GDPR Art. 28 |
| [build-speed-and-libraries.md](build-speed-and-libraries.md) | F21 e-invoicing libraries, F22 KSeF clients, F23 open-source booking/invoicing bases, F24 METR evidence, F25 build-time claims |
| [costs-and-ops.md](costs-and-ops.md) | F16 BaseLinker API, F18 Paddle and fees, F19 KSeF offline modes, F20 API churn, F26 LLM prices, F27 LLM cost estimate |

## Feasibility readings of recurring themes (my judgement, not scores)
Indicative L7 band per theme given the findings; T12 must score the concrete ideas. "Cap" is the highest L7 score the evidence allows for the theme.

| Theme (from lenses 1–6) | Gate / risk | Indicative L7 cap | Findings |
|---|---|---|---|
| KSeF **receive-side** tools (inbox, notifications, archive, matching, PDF rendering) | Self-serve API, rate limits, certificate handling, GDPR processor | 4 | F02, F03, F22, F28 |
| KSeF **issue-side** tools (invoicing, corrections wizard) | Offline modes, QR, certificates; tax-advice boundary | 3 | F19, F20, F14 |
| German E-Rechnung reader/validator/generator (files only) | Libraries exist, no AP needed; crowded | 5 (build) / feasibility not the problem | F21, F04 |
| Peppol **transmission** (own access point) | EUR 3,000+ first year, audits | 2 | F04 |
| Allegro seller tools | API application may be refused; terms change | 3 | F01 |
| BaseLinker / WooCommerce add-ons | Self-serve token; plugin review 2–4+ weeks | 4 | F16, F08 |
| Shopify apps | Review 3–6 weeks in 2026 | 3 | F05, F15 |
| Salon / clinic booking | Payments for deposits cross the licence line unless via Stripe Connect; clinical features approach MDR | 3 (booking only), 1 if it holds money | F09, F10, F13 |
| Open-banking cash-flow tools | AISP registration or licensed aggregator | 2 | F11 |
| LLM-based document tools | Cheap to run; AI-Act label; sub-processors | 4 | F12, F26, F27, F28 |
| Native mobile apps | 12 testers, Apple 4.2 | 2 | F06, F17 |
| Compliance/NIS2/CRA checklists | Not researched in this lens (see Gaps) | n/a | — |

## Seeds
Idea sketches inspired by findings; none validated. Each notes the feasibility angle only; price, competition and demand come from the other lenses. Overlap with seeds from lenses 1–6 is flagged.
1. **Read-only KSeF inbox for micro-firms and bookkeeping offices**: pull purchase invoices via package export into a local mirror, push notifications, accept/query workflow, no issuing. Feasibility advantages: self-serve API, no offline modes, testable on the DEMO environment. [L7-F02](api-access.md), [L7-F03](api-access.md), [L7-F19](costs-and-ops.md). Overlaps lens 6 seeds 1–3 and lens 5 seed 1.
2. **KSeF XML → PDF rendering service (Docker + API, Java/Node/Python)**: pure function, fully automatable tests against FA(3) samples. [L7-F22](build-speed-and-libraries.md), [L7-F02](api-access.md). Overlaps lens 6 seed 4; risk: the Ministry improves its own renderer.
3. **Maintained order-automation add-ons on BaseLinker's API** (reports, label/invoice automation) sold as customer-token SaaS, avoiding Allegro key approval. [L7-F16](costs-and-ops.md), [L7-F01](api-access.md). Check BaseLinker's terms first (unverified).
4. **Chrome extension for one seller or accountant panel with narrow host permissions**: 1–3 week release path, predictable review. [L7-F07](api-access.md). Distribution belongs to lens 8.
5. **WooCommerce–KSeF/invoice bridge sold directly (own site) and listed on WordPress.org in parallel**, so the review wait does not block first sales. [L7-F08](api-access.md). Overlaps lens 2 seed 8.
6. **German E-Rechnung inbox (read XRechnung/ZUGFeRD, validate, archive, export)** assembled from Mustang/KoSIT/phive; no Peppol AP. [L7-F21](build-speed-and-libraries.md), [L7-F04](api-access.md). Overlaps lens 6 seed 7; crowded (lens 6 F16).
7. **Document-extraction API for Polish accounting offices (LLM, per-document pricing)**: cost per document about USD 0.001–0.02 (estimate), needs DPA and AI-Act labelling. [L7-F27](costs-and-ops.md), [L7-F28](licensing-and-regulation.md), [L7-F12](licensing-and-regulation.md).
8. **Booking page for clinics/physios with strictly administrative scope and Stripe Connect deposits**: stay outside MDR by intended purpose; no pooled funds. [L7-F13](licensing-and-regulation.md), [L7-F10](licensing-and-regulation.md). Overlaps lens 6 seed 5, lens 1 salon seeds.
9. **GDPR/DPA and sub-processor pack generator for small SaaS and accountants** (templates plus register): a document product with no regulatory licence, based on Art. 28. [L7-F28](licensing-and-regulation.md). Demand unverified.
10. **Trust-and-compliance "feasibility checker" for builders**: a free checklist/site listing API terms, review times and licence gates per platform (F01, F05, F15, F06), as a lead-gen asset for developer audiences. Weak monetisation; flagged for T11 as a content play.

## Coverage
Counted from this session (2026-10-29), ±2.
- **Web searches (WebSearch tool): 15 calls**, Polish 5, English 10. Topics: KSeF 2.0 integrator requirements, OpenPeppol access point fees and accreditation, KNF payment institutions (MIP/KIP), AISP registration, Stripe Connect licensing, EU AI Act Article 50 dates, MDR software qualification, tax-advice monopoly, METR productivity studies, solo-founder MVP timelines, KSeF outages, Shopify review times. German search not run (see Gaps).
- **Pages fetched with usable content: 24.** developer.allegro.pl (documentation, rules), CIRFMF/ksef-docs (README, srodowiska, limity-api, tokeny-ksef, uwierzytelnianie via raw GitHub), ksef.podatki.gov.pl notice, peppol.org fees, shopify.dev (checklist, revenue share), Shopify developer forum thread, Google Play Help, Chrome Web Store docs, WordPress developer FAQ, rpms.pl, docs.stripe.com Connect overview, Goodwin alert, metr.org post, gdpr-info.eu, Paddle pricing, Apple guidelines, BaseLinker API, Infor offline-mode article, buildthisnow.com. Search-result summaries only (page not read): comparic.pl, e-prawnik.pl, openregulatory.com, eli.gov.pl tax-advice act, Infor API-compat article, avask.com.
- **API queries:** GitHub repo API for 12 repositories and 3 language searches; OpenRouter model list (457 models, about 35 priced entries inspected); HN Algolia (2 queries, 0 usable hits).
- **Countries:** Poland (F01–F03, F09, F11, F14, F16, F19–F20, F22), EU/Germany (F04, F12, F13, F21, F28), US/global platforms (F05–F08, F10, F15, F17–F18, F24–F27). Not covered: Czechia, Nordics, Baltics, Netherlands, France, Italy, Spain, Brazil, India.
- **Sectors:** marketplaces and e-commerce (F01, F05, F15, F16), tax/e-invoicing (F02–F04, F19–F22), payments (F09–F11), healthcare administration (F13), app stores (F06, F07, F17), AI/LLM (F12, F24–F27), data protection (F28).
- **Searches that found nothing or little:** AISP registration conditions in Poland (only generic KNF pages); Stripe's own statement on PSD2 licence position for platforms; official KSeF taxpayer or outage notices for 2026; exact KSeF token/certificate sunset date (only a secondary source); Cal.com repository facts (redirect); Shopify's official review SLA; Apple annual fee page; HN threads of solo builders with dates; ops/support-load data for solo SaaS (nothing verifiable found).
- **AI-directed text:** none seen on the fetched pages, apart from a "Copy for AI" button label and heavy self-promotion on the Build This Now page (F25), which is why that finding is marked low reliability.
- **Data-quality flags:** (a) many pages were read through a summarising fetch tool, not word for word: quoted article numbers (Allegro terms) and figures should be re-checked against the original before they are used in a customer-facing claim; (b) the Shopify wait times are forum anecdotes from spring 2026; (c) GitHub licence "NOASSERTION" only means the classifier gave up; (d) USD figures are not converted to PLN.

## Gaps
1. **Compliance product feasibility** (NIS2/CRA checklists, pay-transparency, ESG reporting, EAA accessibility): no regulatory-exposure or "are we giving legal advice" research done for these themes from lens 5. Next: Polish KSC amendment text and Ministry of Digital Affairs pages.
2. **Current Allegro API practice:** which features need the "100 users"/partner route, rate limits, user-agent/captcha rules from 2025. Next: developer.allegro.pl rules/user-agent pages, the Allegro API GitHub issue tracker (lens 6 F10).
3. **Peppol in Poland:** whether Poland's KSeF-first approach makes any Peppol transmission demand likely; resale prices of AP providers. Next: provider API pricing pages.
4. **Payments:** Stripe/Przelewy24/PayU terms for platforms (marketplace deposits), PSD2 position of a Connect platform in Poland, Polish AISP conditions. Next: the Ustawa o usługach płatniczych text on ISAP, KNF FAQ, a written answer from Stripe support.
5. **Shopify and App Store waits today** (Oct 2026), "unlisted"/custom distribution for faster first sales, Apple fee and organisation rules. Next: Shopify community category, Apple enrollment help.
6. **Ops/support burden with numbers:** hours of support per 100 customers for a solo SaaS, incident frequency. Next: Indie Hackers and Starter Story interviews (unreachable here), founder blogs with revenue and hours.
7. **Verified solo AI-built MVP case studies with dates:** only two self-reported cases found (F25). Next: Show HN "I built X in N weeks" posts, IndieHackers milestones, TrustMRR founder notes.
8. **German, Czech, French, Spanish primary sources** for local gatekeepers (DATEV Marktplatz, Pohoda/iDoklad partner APIs, Chorus Pro) were not searched; DATEV and similar partner programmes may be a major hidden gate for DACH products.
9. **Library quality:** community KSeF clients and Mustang were not run or code-reviewed; stars are not quality.
10. **Terms of third-party tools used as platforms** (BaseLinker, Fakturownia, wFirma API terms) for commercial add-ons were not read.
