# R10 Latin America (OECD) (T14): patterns and coverage

Chile, Mexico, Colombia, Uruguay, Costa Rica (scanned in that order). All sources accessed **2026-11-02**. Catalogue: [../../../catalogue/R10-latin-america.csv](../../../catalogue/R10-latin-america.csv), **41 rows** (CL 10, MX 13, CO 8, UY 6, CR 4), each with a traction figure (or an explicit "no figure found") and its source.

## Files

| File | Content |
|---|---|
| [chile.md](chile.md) | regional legal AI (Magnar, Lemontech LIA), SII-connected SME accounting (Cenit), WhatsApp CX/sales agents (Vambe, Chattigo, Wots), HR/payroll agents (Buk AI), clinic scheduling agents (Cero, Eniax), sales-call AI (Diio) (CL-001…010) |
| [mexico.md](mexico.md) | broker agents (Handle), SAT tax filing (Heru), Mexican legal AI (LEXIMEX, AIJusticia), enterprise agent layer (Primero), SME POS agents (Órale AI, Pulpos), chart apps (Finno, EvidenceMD), Crabi, Nuvo AI, Yavendió, Leracom (MX-001…013) |
| [colombia.md](colombia.md) | clinical AI (Telepatia), pay-per-meeting sales agents (Dapta), anti-counterfeit agents (Signa), restaurant vision (Emilia AI), Truora, Celes, Kebo, Innovaitors (CO-001…008) |
| [uruguay.md](uruguay.md) | WhatsApp super-assistant (Zapia), collections agents (Mozart), agent platform (Roma AI), insurance-broker AI for the EU (Foliume), US dealer agents (Flai), GeneXus Next (UY-001…006) |
| [costa-rica.md](costa-rica.md) | Huli AI clinical notes, Avify, Indax, Dataizen; reason for fewer than 5 (CR-001…004) |

## Choices recorded
- IDs `R10-<ISO>-NNN`, numbered per country. Each row's `pl_adaptation_angle` starts with `adapts: <Western product>; PL: <entered / no / unknown>`, as in T10–T13. **No R10 product was confirmed in Poland.** Foliume (UY-004) already sells to Spanish, German and Portuguese insurers, so it is the one EU-entry item to recheck in T16–T18.
- `works_in_polish`: no product was tried hands-on (time budget). "no" where the product is bound to Spanish-language national law, tax systems or local hospital systems; "unknown" for generic apps.
- Domicile: companies headquartered abroad but built by founders from the country and first grown there are filed under that country, with a note: Handle (SF, first market Mexico), Telepatia (now São Paulo, launched in Colombia), Flai (SF, Uruguayan founders), Nuvocargo (NY, US–Mexico corridor). Yavendió (HQ unverified, likely Peru) is filed under Mexico, its stated growth market. EvidenceMD and Finno (seller domicile unverified) are filed under the Mexican chart where they rank. Cenit is Chilean even though its press coverage is Mexican.
- Not catalogued because they are based outside R10 even though they sell mainly in R10: Darwin AI (Brazil), Patagon AI and Jelou (Ecuador), Juztina (Peru), Nuvia, Sharpi and Tako (Brazil).
- Product URLs: where the homepage could not be confirmed (Handle, Primero, Signa, Emilia AI, Mozart, Roma AI, Flai, Wots, Indax, Innovaitors), the `url` column holds the source article, as in R8/R9. Two chart apps use their App Store listing.
- Rows with no or unconfirmed LLM core, kept for a local pattern and flagged: Cero, Eniax, Finno, Celes, Avify, Dataizen. That is 6 of 41.
- Weak-traction rows (pre-seed/seed only, award listing only, or no figure): Wots, LEXIMEX, AIJusticia, Leracom AI, Órale AI, Yavendió, Pulpos, Emilia AI, Innovaitors, Indax, Dataizen. That is 11 of 41. T15 should weight them low. LEXIMEX and AIJusticia are kept because they add Mexico to the national-legal-AI spread count.
- Hype markers kept on purpose: Kebo (one of six "AI finance assistant" apps in the Colombian Finance chart), EvidenceMD (possible wrapper).

## Poland signal
1. **SME accounting connected to the tax authority, with a human expert behind the AI**, now appears in three R10 countries. Cenit (Chile) reports "+7,000 pymes" paying from CLP 16,990/month and files the monthly F29 from SII data; its Mexican RESICO product reports 4x month-on-month growth in 2026 with 85% of users filing without an accountant (company claims). Heru (Mexico) does the same for SAT freelancers and is backed by Google's Gradient Ventures. Cifrato (Colombia, R0) does it for DIAN. Each one is built on a national e-invoicing feed (SII DTE, SAT CFDI, DIAN factura electrónica) and the monthly filing it enables. Poland's equivalent trigger is **KSeF** (mandatory from 2026): an AI bookkeeping service for JDG and small sp. z o.o. that reads KSeF invoices, prepares JPK_V7 and ZUS, and escalates edge cases to a partner biuro rachunkowe. Phase 1 found KSeF tooling crowded; the R10 lesson is that the **outcome** (the monthly filing done, with an accountant's guarantee, at a fixed price) is what sells, not the invoice tool. T16 should check Polish players (inFakt, wFirma, Fillup, ifirma) for AI-led filing.
2. **Clinical documentation AI sold to institutions** spreads fast in Spanish- and Portuguese-speaking systems. Telepatia (Colombia) went from launch in 2025-07 to a USD 33M a16z Series A in 2026-06, with >14M patients through >25 institutions and a presence in 9 of the top 10 Colombian hospitals (excerpt). Huli (Costa Rica) added AI notes to an EMR with >2,500 doctors. Together with Abridge (R0), Heidi (R8) and others this is now a ≥5-country, ≥3-region theme. The Polish adaptation needs P1/gabinet.gov.pl EDM, e-recepta, ICD-10 and NFZ reporting. The risks: Docplanner (Polish-rooted) already ships an AI notes assistant (to verify), and medical-device rules apply.

## Cross-country patterns
1. **WhatsApp sales and CX agents** draw the most rounds: Vambe USD 14M, Dapta USD 6M, Chattigo (acquired for ~USD 60M at >USD 10M ARR), Yavendió, Wots, Leracom, Pulpos, Roma AI, Truora, Avify. Ten rows in 5 countries. The moat is WhatsApp-centred buying behaviour, which **does not transfer to Poland** (phone, email, Messenger, Allegro chat). Dapta's pricing per qualified meeting is the transferable part (durable signal 7).
2. **National-law legal AI**: Magnar (CL, 350 firms in 7 countries in about a year, about to open in Mexico), Lemontech LIA (CL), LEXIMEX and AIJusticia (MX). This repeats R9 (Jupytr, Apilex), R7, R8 and R6. **Regional expansion is fast**: Magnar enters a country by loading its law and signing a local law firm as an investor/partner, as Apilex is doing in the EU. That is an entry-risk pattern for Poland as well as a template.
3. **Tax-authority-connected filing for SMEs and freelancers** (Cenit, Heru, Cifrato): see Poland signal 1.
4. **Clinical AI scribes and decision support** (Telepatia, Huli, EvidenceMD) and **clinic scheduling/no-show agents** (Cero >1M appointments/month, Eniax): see Poland signal 2.
5. **Agents inside a vertical workflow or system of record**: insurance brokers (Handle in MX, Foliume in the EU), HR/payroll (Buk AI payroll auditor), car dealers (Flai), freight (Nuvo AI), SME POS (Pulpos, Órale AI). Repeats R8/R9.
6. **Collections and enforcement agents**: Mozart (debt negotiation, >50 corporate clients, 15 countries), Signa (undercover counterfeit purchases, USD 138k MRR). New in the catalogue. For Poland: windykacja polubowna under UOKiK rules, and Allegro/OLX counterfeit evidence packs for brand owners.
7. **Consumer WhatsApp super-assistant** (Zapia, >6M users): LLM-native, but exposed to Meta's platform and to Meta AI. Weak for Poland.
8. **Export-first teams from small markets** (Uruguay: Flai, Foliume, Mozart; Chile: Magnar) sell abroad from the start, as Israel (R8) and Turkey (R9) do.

## Products also in R0–R9 (spread signal)
Not re-catalogued, seen in R10 charts or sources: **Cifrato** (R0-CO-093, Colombian, the DIAN accounting agent), **Plaud** (R1-US-054; Productivity #10–15 in CL, CO, CR, MX, UY), **Manus** (R0-SG-011; #16–63 in all 5), **Perplexity** (R0-US-008; all 5), **Praktika** (R2-GB-029; Education #9–25 in all 5), **Loora** (R6/R7; Education #3–11 in all 5), **Astra AI** (R6-SI-001; Education #7–61 in all 5), **Knowunity** (R3-DE-009; #20–48), **Owll Translator** (R7-SG-004; CL Business #18, UY #49), **Lovable** (R0-SE-005; CL, CR), **Sintra** (R4-LT-001; UY #95), **Fluently** (R3; MX, CL, UY). **MediSearch AI** (Medical #1 MX, #2 CL, #4 CO) and **Learna AI** (Education #2 in all 5) are not in any catalogue; both look like global apps and are left to T15. Theme repeats: national legal AI (Magnar/LEXIMEX vs Harvey, Legora, Jupytr), clinical scribes (Telepatia/Huli vs Abridge, Heidi), tax filing (Heru/Cenit vs TaxDown, Keeper), vertical agents in a system of record (Handle/Foliume vs Sixfold).

## Polish adaptation angles from R10 (for T15–T18)
- **AI bookkeeping with a guaranteed monthly filing** for JDG/small sp. z o.o. on KSeF + JPK_V7 + ZUS, with a partner biuro rachunkowe (Cenit, Heru, Cifrato).
- **Clinical scribe for NFZ poradnie and private gabinety** writing into P1/EDM with e-recepta and ICD-10 (Telepatia, Huli).
- **No-show and waiting-list agent** for NFZ-contracted clinics: SMS/phone confirmations and slot reallocation (Cero, Eniax).
- **Legal research and drafting on SAOS/ISAP with citation verification** against the law text (LEXIMEX's citation check, Magnar's Word integration).
- **Agent for insurance multiagencje** across PZU/Warta/Ergo Hestia portals and OWU documents (Handle, Foliume).
- **Payroll auditor agent** checking Kodeks pracy, ZUS DRA/RCA, PPK and PIT-11 before payroll close (Buk AI).
- **Polite debt-collection negotiation agent** within UOKiK guidance, with KRD/BIG integration (Mozart).
- **Counterfeit evidence packs** from Allegro/OLX/Vinted for brand owners and pharma (Signa).
- **Service-appointment and reminder agent for car dealers/ASO**, phone-first (Flai).

## Coverage

| Country | Status | New rows | R0–R9 overlaps seen | Products researched | Sources read | Searches | Notes |
|---|---|---|---|---|---|---|---|
| Chile | done | 10 | 9 (Plaud, Manus, Perplexity, Praktika, Loora, Astra AI, Knowunity, Owll, Lovable) | ~18 | 9 pages + 5 feeds | 4 + site search | legal AI and SII-connected accounting are the local champions |
| Mexico | done | 13 | 8 (Plaud, Manus, Perplexity, Praktika, Loora, Astra AI, Knowunity, Fluently) | ~24 | 11 pages + 5 feeds | 7 (6 Spanish) + site search | most VC rounds; Mexican legal AI has no public traction |
| Colombia | done | 8 | 8 (Cifrato, Plaud, Manus, Perplexity, Praktika, Loora, Astra AI, Knowunity) | ~18 | 9 pages + 5 feeds | 4 (3 Spanish) + site search | Telepatia is the region's best-funded vertical AI |
| Uruguay | done | 6 | 7 (Plaud, Manus, Perplexity, Praktika, Loora, Astra AI, Sintra) | ~13 | 7 pages + 5 feeds | 2 + site search | export-first teams; Zapia the only R10 LLM app in any chart |
| Costa Rica | done (thin) | 4 | 6 (Plaud, Manus, Perplexity, Praktika, Loora, Astra AI) | ~10 | 5 pages + 5 feeds | 3 + site search | high AI use, near-zero AI startup funding |
| **R10** | done | **41** | 13 distinct | ~83 | 41 pages + 25 feeds | 20 + 5 site searches | |

- Region total **41** is just above the 40–80 floor. Reasons it is not higher: Costa Rica yields 4 rows (no local AI funding found), Uruguay's AI firms are few and mostly export-first, many LatAm AI startups that sell into R10 are Brazilian, Argentine, Ecuadorian or Peruvian and were excluded, and the one-hour budget limited depth. 11 rows are weak and 6 lack a confirmed LLM core.
- App Store top-grossing feeds read for all 5 countries × 5 genres (Business 6000, Productivity 6007, Education 6017, Finance 6015, Medical 6020) on 2026-11-02. iTunes lookups failed (empty responses), so app details come from the feed summaries. Similarweb Google Play pages, LAVCA data, Start-Up Chile and iNNpulsa cohorts, ANII/CUTI lists and PROCOMER were **not screened**. Most funding facts come from LatamList articles that were read in full; figures from search summaries are marked "excerpt".
- Durable signals: mostly 1 (replaced spend: associates, contador fees, call-centre agents, documentation time), 2 (daily/monthly obligations), 8 (national legal corpora, tax-authority feeds, hospital and insurer systems), 7 (per-meeting, per-table, per-conversation pricing). Retention evidence is thin: Chattigo's >USD 10M ARR over ~10 years and Telepatia's institution-wide rollouts are the strongest. No cohort retention or NRR figure was found for any R10 product. Hype warnings: solo-developer "AI finance" apps (CO), possible wrappers (EvidenceMD), registered-but-not-paying user counts (Dapta, Zapia), sponsored-content metrics (Huli), Meta platform risk (Zapia).
- Searched and found nothing: LLM products for Chile's Dirección del Trabajo, CBR property records or Fonasa/Isapre; Mexico's IMSS/Infonavit employer filings, notarías or Registro Público; Colombia's tutela/derecho de petición, renta filing (Tributi) or EPS authorisations; Uruguay's BPS/DGI; Costa Rica's TRIBU-CR or CCSS employer filings; any public cohort retention curve.
- Link check: see the T14 line in [PROGRESS.md](../../../PROGRESS.md).
