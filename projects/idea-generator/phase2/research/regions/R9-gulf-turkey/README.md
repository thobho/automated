# R9 Gulf & Turkey (T13): patterns and coverage

Turkey, United Arab Emirates, Saudi Arabia, Qatar, Kuwait, Bahrain (scanned in that order). All sources accessed **2026-11-01**. Catalogue: [../../../catalogue/R9-gulf-turkey.csv](../../../catalogue/R9-gulf-turkey.csv), **40 rows** (TR 11, AE 9, SA 16, QA 2, KW 1, BH 1), each with a traction figure and its source.

## Files

| File | Content |
|---|---|
| [turkey.md](turkey.md) | national case-law legal AI (Jupytr, Apilex, Safahat, Leagle), Turbo Law, teacher paperwork (Öğretmen Evrak), property reports (Tapusor), app studios (Codeway, FERASET), Bolt Insight, Jotform AI Agents (TR-001…011) |
| [united-arab-emirates.md](united-arab-emirates.md) | Arabic enterprise AI (Arabic.AI, CNTXT/Munsit), e-commerce agents (qeen.ai), legal AI (Qanooni, Legaline), HR/payroll (Bayzat), state agent (TAMM AutoGov), proptech (Prop-AI, Coraly) (AE-001…009) |
| [saudi-arabia.md](saudi-arabia.md) | Arabic CX and voice agents (Lucidya, Intella, Wittify, Sawt, Velents), HUMAIN Chat, legal AI (Mohami, Aqood, Malakah), restaurant POS agents (TabSense), teacher-admin apps on Noor (Shawahid, Al-Mu'allim, Al-Muwajjih), exam prep and study apps (SA-001…016) |
| [qatar.md](qatar.md) | Fanar national LLM, ShipBee; reason for fewer than 5 (QA-001…002) |
| [kuwait.md](kuwait.md) | Wkeel AI; reason for fewer than 5 (KW-001) |
| [bahrain.md](bahrain.md) | Bahrain Chamber's Issa assistant; reason for fewer than 5 (BH-001) |

## Choices recorded
- IDs `R9-<ISO>-NNN`, numbered per country. Like T10–T12, each row's `pl_adaptation_angle` starts with `adapts: <Western product or 'no single leader'>; PL: entered / no / unknown`. **No R9 product was confirmed in Poland.** Apilex.ai (TR-002) plans DE/FR/ES/IT entry in 2026, so it is the one EU-entry item to recheck in T16–T18.
- `works_in_polish`: no product was tried hands-on (time budget). "no" where the product is bound to Turkish/Arabic law, dialects or state systems; "unknown" for global apps.
- Turkish-founded companies selling mainly abroad are filed under Turkey with `country_specific = n` (Turbo Law, Bolt Insight, Jotform, Codeway), as R8 did for Israel. **reprai** (Webrazzi-covered, site says Delaware) and **fal.ai** (infrastructure) are not catalogued.
- Study apps with unverified domicile are filed under the chart where they rank highest: AcadAI and Bites under Saudi Arabia.
- State/national products catalogued like Pair (R7) and NSWEduChat (R8): TAMM AutoGov (AE-007), HUMAIN Chat (SA-003), Fanar (QA-001), Issa (BH-001).
- Product URLs: where the homepage did not resolve or could not be confirmed (Jupytr, Legaline, Aqood, Sawt, Leagle, Issa), the `url` column holds the source article, as in R8. The teacher and exam apps use their App Store listing.
- Rows with no or unconfirmed LLM core, kept for a local pattern and flagged in `llm_role`/`hype_warnings`: Öğretmen Evrak (TR-005), Shawahid (SA-010), Al-Mu'allim (SA-011), Mujtahid (SA-013), ShipBee (QA-002). That is 5 of 40.
- Weak-traction rows (pre-seed/seed/accelerator only, launch only, or <100 ratings): Safahat, Leagle, Qanooni, Legaline, Prop-AI, Coraly, Mohami, Aqood, Malakah, Wittify, Sawt, Velents, Al-Muwajjih, ShipBee, Wkeel, Issa. That is 16 of 40, more than R8 (9), because Gulf rounds are small and early. T15 should weight them low. Leagle (TR-011) and Malakah (SA-016) were added to reach the 40-row floor; both strengthen the legal-AI spread count rather than adding new themes.
- Hype markers kept on purpose: Chat & Ask AI (Codeway), FERASET.

## Poland signal
1. **National case-law legal AI is now a 5-country pattern in one region**: Turkey (Jupytr, Apilex, Safahat, Leagle), UAE (Qanooni, Legaline), Saudi Arabia (Mohami, Aqood, Malakah), Kuwait (Wkeel). The best-evidenced one, **Jupytr**, reports ~100 firms and corporates paying 4,490–11,900 TL per user per month within ~7 months, and firms moving to it **from Harvey and Legora**. The local corpus and local document formats beat the global leader. Apilex now plans to enter four EU markets. For Poland this supports a legal research and drafting assistant built on SAOS, orzeczenia.ms.gov.pl, ISAP and Polish pleading formats, distributed through izby radców prawnych (Leagle's bar-association route). The risks: a foreign national-corpus player (Apilex) or a Polish incumbent (LEX/Legalis) moving first. T16 should check Wolters Kluwer LEX and C.H. Beck Legalis AI features.
2. **Teacher paperwork is a paying consumer niche in two state school systems**: Saudi Arabia (Shawahid #3 grossing in Education; Al-Mu'allim #16, Al-Muwajjih #22, Taqrir #29, all built around the ministry's Noor system and evaluation "evidence") and Turkey (Öğretmen Evrak, #20, 5,606 ratings, five years in the chart). Most are templates; only Al-Muwajjih uses an LLM. **An LLM-native version is open.** The Polish analogue: documentation for ocena pracy and awans zawodowy, IPET/WOPFU, dziennik pedagoga/psychologa, uzasadnienia ocen and e-dziennik (Librus/Vulcan) exports, sold B2C to teachers (~700k in Poland, to verify) with a free tier. Risks: EU AI Act (education is high-risk only for scoring/admission, not paperwork drafting; check) and RODO for pupil data (Al-Muwajjih keeps data on the device).

## Cross-country patterns
1. **National legal-corpus assistants** (see Poland signal 1): 10 rows in 4 countries. Repeats R7 (LegalOn), R8 (Lawpath AI, MiAI Law), R6.
2. **Teacher and school-staff paperwork** (see Poland signal 2): 4 rows in 2 countries plus 2 seen. New in R9.
3. **Dialect speech and customer-service agents** get the most VC (CNTXT USD 60M, Lucidya USD 30M, Intella USD 12.5M, Wittify, Sawt, Velents). Same theme as Wonderful (R8), Born Digital (R6), PolyAI (R2); the moat is the dialect.
4. **Sovereign national LLMs and state assistants** (HUMAIN Chat, Fanar, TAMM AutoGov, Arabic.AI with HUMAIN money). Same as PLLuM/Bielik in Poland: not a founder opportunity, but they raise the baseline for "Polish-language" claims.
5. **Agents inside a vertical system of record**: TabSense (restaurant POS, 1,000+ clients in about a year via STC/Zain), Bayzat (payroll with WPS), Tapusor (property data). Repeats R8 (Xero JAX, Employment Hero).
6. **Real-estate agency and investor automation** (Coraly, Prop-AI, Tapusor): repeats R1/R8. The Polish moat is EKW, RCiWN and MPZP data.
7. **Telco and chamber distribution** (TabSense via STC/Zain, Velents via stc Bahrain, Issa via the Bahrain Chamber): a channel lesson for Polish SME products (Orange/Play business bundles, izby gospodarcze, cechy).
8. **National exam prep** (Mujtahid for Qiyas; Turkey's driving-licence and KPSS apps): repeats R8 (PTE, psychometric) and R7.
9. **App studios and AI trading-signal apps** (Codeway, FERASET; trading-signal apps in AE/KW/BH Finance charts): hype markers.

## Products also in R0–R8 (spread signal)
Not re-catalogued, seen in R9 charts or sources: **Manus** (R0; SA Productivity #4, AE #11, TR #31), **Plaud** (R1; TR #19, AE #13, SA #23), **Perplexity** (R0; TR, AE, SA top 10), **Lovable** (R0; AE #29, SA #31), **Genspark** (R0; SA #24), **Praktika** (R2; TR #13, AE #10, SA #12), **Astra AI** (R6-SI-001; TR Education #3), **Owll Translator** (R7-SG-004; TR Business #27), **PMcardio** (R6-SK-003; TR, AE, SA Medical top 15), **Pocket** (R2; AE #17), **Turbo AI** (R7/R8; AE #29), **Speak** (R1/R7; TR, AE, SA top 3), **Chartnote** (R1-US-012; KW Medical #24), **SEOBOT** (R0-TR-024) and **Freya** (R0-TR-089) are Turkish. Theme repeats: national legal AI (Jupytr/Apilex vs Harvey, Legora, Spellbook, LegalOn, Lawpath), dialect CX agents (Lucidya/Intella vs Wonderful, PolyAI, Born Digital), state LLMs (HUMAIN/Fanar vs Pair, Bürokratt, NSWEduChat), vertical agents in a system of record (TabSense/Bayzat vs Xero JAX, Employment Hero).

## Polish adaptation angles from R9 (for T15–T18)
- **Legal research and drafting assistant on SAOS/ISAP** with Polish pleading templates and Word track changes, sold per seat to kancelarie and in-house teams through izby radców prawnych (Jupytr, Apilex, Leagle).
- **Teacher documentation assistant**: ocena pracy/awans, IPET/WOPFU, dziennik pedagoga, uzasadnienia ocen, e-dziennik exports; privacy-first (Shawahid, Al-Muwajjih, Öğretmen Evrak).
- **Abonament prawny for JDG/SMEs** with AI triage and radca review (Mohami).
- **Gastronomy POS/back-office agent** with KSeF, food cost and delivery-platform menus, sold through a telco or payment partner (TabSense).
- **Employee HR/payroll Q&A** over Kodeks pracy, ZUS, PPK on top of Polish payroll systems (Bayzat AI).
- **Property report from EKW + RCiWN + MPZP** for buyers and investors (Tapusor, Prop-AI).
- **AI help desk for izby gospodarcze/cechy** for their SME members (Issa).
- **Migrant legal tasks matched to radcy prawni** with AI scoping in UA/RU/EN (Legaline).

## Coverage

| Country | Status | New rows | R0–R8 overlaps seen | Products researched | Sources read | Searches | Notes |
|---|---|---|---|---|---|---|---|
| Turkey | done | 11 | 9 (Manus, Plaud, Perplexity, Praktika, Astra AI, Owll, PMcardio, Speak, SEOBOT/Freya) | ~23 | 5 pages + 5 feeds | 10 (5 Turkish) | strongest legal-AI evidence; Startups.watch/egirişim not screened |
| United Arab Emirates | done | 9 | 7 (Manus, Plaud, Perplexity, Lovable, Praktika, Pocket, Turbo AI) | ~22 | 2 pages + 5 feeds | 7 (1 Arabic) | money goes to Arabic infrastructure; local vertical champions few |
| Saudi Arabia | done | 16 | 7 (Manus, Plaud, Perplexity, Lovable, Genspark, Praktika, PMcardio) | ~30 | 4 pages + 5 feeds | 5 + shared | teacher-admin finding came from App Store charts |
| Qatar | done (thin) | 2 | 0 new | ~7 | 5 feeds | 3 | sovereign AI, few startups; QSTP bot-blocked |
| Kuwait | done (thin) | 1 | 1 (Chartnote) | ~8 | 1 page + 5 feeds | 2 | no Kuwaiti gen-AI round found |
| Bahrain | done (thin) | 1 | 0 new | ~7 | 2 pages + 5 feeds | 3 | cloud/regulatory hub; foreign AI via telco partners |
| **R9** | done | **40** | 15 distinct | ~97 | 14 pages + 30 feeds | 30 + shared | |

- Region total **40** is at the 40–80 floor. Reasons it is not higher: Qatar, Kuwait and Bahrain together yield 4 rows (small populations; AI money goes into sovereign models and outbound investment; no local gen-AI rounds found); Gulf rounds are mostly pre-seed, so 16 rows are weak; the one-hour budget limited depth; most figures come from search excerpts (marked).
- App Store top-grossing feeds read for all 6 countries × 5 genres (Business 6000, Productivity 6007, Education 6017, Finance 6015, Medical 6020) on 2026-11-01, plus 26 iTunes lookups for ratings, release dates and descriptions. Similarweb Google Play pages, MAGNiTT data, Startups.watch, Hub71/Flat6Labs/Misk/Monsha'at cohorts, Tamkeen, KFAS and QSTP lists were **not screened**.
- Durable signals: mostly 1 (replaced spend), 2 (frequent problem with an owner), 8 (local corpus/dialect/state-system integration), 5 (telco, chamber, bar-association channels). Retention evidence is weak: Öğretmen Evrak and Bites still top-grossing years after launch; Jupytr reports switching from Harvey/Legora. No cohort retention, NRR or ARR figure was found for any R9 product. Hype warnings: app studios (Codeway, FERASET), AI trading-signal apps, self-reported usage numbers (qeen.ai, Prop-AI, Lucidya), and state products with no usage data (HUMAIN Chat, Fanar).
- Searched and found nothing: LLM products for Turkish e-fatura/e-defter, mali müşavir or SGK payroll; UAE corporate tax/VAT, Emiratisation or health-insurance claims; Saudi ZATCA e-invoicing/zakat, Qiwa/GOSI, Nitaqat or NPHIES claims; any generative assistant in Kuwait's Sahel or Bahrain's MyGov; any public cohort retention curve.
- Link check: see PROGRESS.md (T13 lines) for the run on all R9 files, the CSV and countries.md.
