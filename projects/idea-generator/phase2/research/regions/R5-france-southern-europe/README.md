# R5 France & Southern Europe (T09): patterns and coverage

France, Spain, Italy, Portugal, Greece, Malta, Cyprus (scanned in that order). All sources accessed **2026-11-01**. Catalogue: [../../../catalogue/R5-france-southern-europe.csv](../../../catalogue/R5-france-southern-europe.csv), **40 rows** (FR 14, ES 7, IT 6, PT 5, GR 4, MT 1, CY 3), each with a traction figure and its source.

## Files

| File | Content |
|---|---|
| [france.md](france.md) | SMB back-office agent, legal research and legal AI (Doctrine, Haiku, Ordalie), scribe, medical phone agent, grading assistant, enterprise agents, AI recruiter, Mistral, consumer tax, revision app, CRE documents (FR-001…014) |
| [spain.md](spain.md) | consumer tax filing (TaxDown), HR suite with agents (Factorial), agent platform, patient follow-up voice agent (Tucuvi), Magnific, SMB voice agent, support agents (ES-001…007) |
| [italy.md](italy.md) | legal AI scaling to Europe (Lexroom), tender bid agent (Cato), skills assessment, student study apps (Kiwi AI, Algor), iGenius/Domyn (IT-001…006) |
| [portugal.md](portugal.md) | Sword Health AI care, customer-ops agents, AI pentest, applied-AI lab; state LLM Amália; Unbabel graveyard (PT-001…005) |
| [greece.md](greece.md) | Greek legal AI, LLM agents for banks, state assistant mAigov, enterprise agents; why Greece is thin (GR-001…004) |
| [malta.md](malta.md) | KYC/onboarding marketplace; OpenAI × Malta national ChatGPT Plus deal; why Malta is thin (MT-001) |
| [cyprus.md](cyprus.md) | Omilia voice AI, hospitality AI recruiting, wellness companion; why Cyprus is thin (CY-001…003) |

## Choices recorded
- IDs `R5-<ISO>-NNN`, numbered per country. FR-013/014 and ES-007 were added after Cyprus to reach the 40-row floor; they come from the same France/Spain searches and have weaker traction (seed rounds, no customer data).
- Products already in R0–R4 are not re-added (listed below).
- `works_in_polish` is `unknown` in every row: no product was tried in this scan (time budget), and no source showed Polish support.
- Rows with unclear or no LLM core are kept where the local pattern matters, and `llm_role` says so: Binderr (MT, AI role unclear), Omilia (CY, CEO says routine queries need no LLM), Doctrine and Factorial (pre-2023 companies with gen-AI layers), mAigov (state assistant). That is 5 of 40.
- mAigov (GR-003) is a state programme, catalogued like Bürokratt in R4 because it decides whether a private citizen assistant has room.
- Omilia is filed under Cyprus because Cyprus Mail counts it in Cypriot funding; TechCrunch calls it Athens-based. Either way it is R5.
- Greece (4), Malta (1) and Cyprus (3) are below 5 products; reasons are in each file and in the Coverage table.

## Cross-country patterns
1. **National legal AI is the strongest country-specific LLM product in R5**, as in R3/R4: Lexroom (IT: 8,000+ firms, 65% daily use, 50M USD Series B, now in ES and DE), Doctrine (FR: 27,000 daily users, bought by RELX/LexisNexis in 2026), Haiku and Ordalie (FR), dikaio.ai (GR). Civil-law players are expanding across Europe, so **Poland is a likely next market** for Lexroom or LexisNexis/Doctrine on top of Libra on LEX (R3). General legal research in Poland counts as taken; niche regulators and regulated professions (notariusze, komornicy, as Haiku targets in France) may not be.
2. **Consumer income-tax filing with AI works at scale in Spain** (TaxDown: 3M+ users, >10M EUR revenue, profitable) and is launching in France (Taxcut, value-based per-filing pricing). In Poland, Twój e-PIT pre-fills most returns for free, so the room is in ulgi, rental income (ryczałt), foreign income for return migrants and the ~1.5–2M Ukrainians, and IKZE/termomodernizacja, not in the basic return.
3. **Voice agents answering phones for health and SMBs** spread in four countries: Vocca (FR, medical practices, distributed via Cegedim), Tucuvi (ES, patient follow-up, 2.5M+ patients, CE IIb), HeyDiga (ES, 80 SMB clients), Omilia (CY/GR, 60M USD ARR in enterprise contact centres). Same theme as fonio (R3) and Installer (R4). In Poland the wedge is integration with practice software and Polish phone habits (rejestracja telefoniczna).
4. **One agent for the micro-business back office**: LegalPlace raised 70M EUR and bought Legalstart to build an agent that does a TPE's accounting and regulatory paperwork on top of a funnel of ~1 in 5 French incorporations. With R3/R4's AI-native accounting firms, this is a strong theme for JDG/sp. z o.o. founders (CEIDG/KRS/S24, ZUS, KSeF, JPK).
5. **Education: curriculum-bound AI wins in national charts.** Ed.ai (FR grading assistant, ~2,500 papers/day, Pronote link), Baobab (FR, Education #6), Kiwi AI and Algor (IT, #17 and #19; Algor serves DSA students under Italian law). States also build their own teacher assistants (France's 20M EUR tender), a Bürokratt-style risk.
6. **Horizontal agent platforms dominate the rest** (Dust FR 20M+ USD ARR, Maisa ES, Twin FR, Automaise PT, Moveo GR, Helvia GR): pattern evidence only, not adaptation targets.
7. **States pick a side on assistants**: Greece built mAigov on Azure OpenAI; Malta gave every eID holder a year of ChatGPT Plus (2026-05); Portugal builds the state LLM Amália; France funds "Territoires d'IA" with Mistral for 100,000 local-government agents. Thin citizen-assistant products have little room; intermediaries and workflows do.
8. **HR suites turn into agent platforms and move into new markets**: Factorial (ES, 16,000+ customers, expanding to DE/FR/IT/PT), Maki (FR), Skillvue (IT), Cleedee (CY, hospitality). Hiring is AI Act high-risk; Polish kadry i płace (ZUS, PPK, L4) is the moat against Factorial.
9. **Graveyard**: Unbabel (PT, AI translation) was reported acquired in 2025 and declared insolvent in 2026-03, an example of an LLM-commoditised category.

## Products also in R0–R4 (spread signal)
Not re-catalogued: **Photoroom** (R0-FR-004), **Parallel** (R0-FR-086), **Sandra AI** (R0-FR-087), **Topo** (R0-FR-094) from France; **Clio** incl. Barcelona's **vLex/Vincent AI** (R1-CA-059); **HappyRobot** (R1-US-040, Spanish founders); **Rillet** (R1-US-028, Greek co-founder); **Knowunity** (R3-DE-009, charts in ES/IT/PT/GR Education); **Sintra** (R4, in MT Productivity chart). Seen in R5 top-grossing charts on 2026-11-01: ChatGPT, Claude, Grok, Perplexity, Plaud, Manus, Lovable (global), Praktika (R2), Loora, Learna, Astra AI. Themes repeating from R1–R4: legal research (Lexroom/Doctrine vs Pandektes/Lexu/Libra), scribes (Nabla vs Tandem/Abridge), voice agents (Vocca/Tucuvi/HeyDiga vs fonio/Installer), SMB back office (LegalPlace vs mika/RoboLabs), consumer tax (TaxDown/Taxcut vs Skatteguiden), state assistants (mAigov/Amália vs Bürokratt/Intric).

## Polish adaptation angles from R5 (for T15–T18)
- **Back-office agent for JDG/sp. z o.o. founders** over CEIDG/KRS/S24, ZUS, KSeF, JPK, sold with biura rachunkowe (LegalPlace).
- **PIT helper beyond Twój e-PIT** for ulgi, najem prywatny, foreign income, migrants (TaxDown, Taxcut).
- **Phone agent for private clinics and dentists** integrated with Polish practice software (Vocca, Tucuvi).
- **AI for regulated professions**: notariusze and komornicy (Haiku).
- **Grading/remediation assistant for Polish teachers** tied to podstawa programowa and e-dziennik (Librus/Vulcan); AI Act high-risk if it scores students (Ed.ai).
- **Study aids for pupils with dyslexia opinions** and CKE accommodations (Algor).
- **Bid-writing assistant for SMEs** on e-Zamówienia/BZP (Cato); the buyer is a private bidder, not the state.
- **KYC/AML file builder** for Polish obligated institutions (Binderr).
- **Seasonal migrant hiring** for hotels and farms with permit paperwork (Cleedee), AI Act high-risk.

## Coverage

| Country | Status | New rows | R0–R4 overlaps | Products researched | Sources read | Searches | Notes |
|---|---|---|---|---|---|---|---|
| France | done | 14 | 4 (R0) | 29 | 14 pages + 4 feeds | 14 | 2 top-up rows with weak traction |
| Spain | done | 7 | 2 (R1) | 18 | 7 pages + 4 feeds | 9 | El Referente 403 |
| Italy | done | 6 | 0 | 14 | 5 pages + 4 feeds | 9 | 2 chart-based rows |
| Portugal | done | 5 | 0 | 11 | 5 pages + 4 feeds | 6 | all 5 horizontal/global; no local champion found |
| Greece | thin | 4 | 1 (R1) | 12 | 5 pages + 4 feeds | 7 | small applied-LLM market; founders build abroad |
| Malta | thin | 1 | 0 | 6 | 1 page + 4 feeds | 3 | ~0.55M people; state–OpenAI deal instead of startups |
| Cyprus | thin | 3 | 0 | 9 | 2 pages + 4 feeds | 3 | app-studio holding location; tiny AI rounds |
| **R5** | done | **40** | 7 | 99 | 39 pages + 28 feeds | 51 | |

- Region total **40** is at the 40–80 floor. Reasons it is not higher: Greece, Malta and Cyprus together yield 8 rows (reasons above); Portugal's scene is horizontal; several French and Spanish leaders already sit in R0/R1; local media were partly blocked (El Referente 403) and searches surfaced aggregators more than primary sources; the one-hour budget limited depth.
- Durable signals: sourced for most rows, mostly 1 (replaced spend), 5 (channel), 7 (pricing), 8 (hard to absorb). Retention/expansion (signals 3/4): Lexroom (65% daily / 94% weekly active; funding x25 in 14 months), Doctrine (27,000 daily users), Dust (ARR ~1M → 20M+ USD in two years), Omilia (ARR x10 since 2020), Ed.ai (paper volume x100+ in 9 months), Factorial (ARR >100M USD, excerpt), LegalPlace (50,000 subscribers, 60%/yr growth), TaxDown (profitable, >10M EUR). Hype warnings: LegalPlace's agent is still a plan; Magnific is close to a multi-model reseller; Kiwi AI's user claim is unverified; Soula's funding figures conflict; Dust not profitable.
- Searched and found nothing: LLM startups with traction for payroll (FR paie, IT/ES nóminas), notaries, syndic/property management, commercialisti/gestorías/contabilistas, public-administration services by private vendors, GESY/SNS/e-prescription admin; any cohort retention or NRR figure. Google Play (Similarweb) charts were not read; accelerator batches (Wayra, Station F, Startup Portugal, Elevate Greece) were seen only through news items.
- Bot-blocked or failed fetches: elreferente.es (403), finder.techleap.nl (403), seedtable.com (403), swordhealth.com (429), mobihealthnews.com (403), digital-skills-jobs.europa.eu (403), gov.gr and mindigital.gr (403).
