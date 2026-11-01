# R8 Oceania & Israel (T12): patterns and coverage

Australia, New Zealand, Israel (scanned in that order). All sources accessed **2026-11-01**. Catalogue: [../../../catalogue/R8-oceania-israel.csv](../../../catalogue/R8-oceania-israel.csv), **40 rows** (AU 16, NZ 8, IL 16), each with a traction figure and its source.

## Files

| File | Content |
|---|---|
| [australia.md](australia.md) | clinical scribes (Heidi, Lyrebird), support agents (Lorikeet), agent builder (Relevance AI), legal AI (Checkbox, Lawpath AI, Isaacus, MiAI Law), tax research for accountants (SavvyWise), NDIS/aged-care admin agents (Minikai), payroll agents (Employment Hero), real-estate AI (Agentsy, RentBetter), state tutor (NSWEduChat), PTE visa-exam apps (AU-001…016) |
| [new-zealand.md](new-zealand.md) | contract review (Ivo), Xero JAX agents, sole-trader tax (Hnry, Solo), meeting-to-document (Contented), finance agents (Sterling), commercial property AI (Re-Leased), SortMe; graveyard Soul Machines (NZ-001…008) |
| [israel.md](israel.md) | local-language support agents (Wonderful), Base44 and Symphony by Wix, legal agents (Chamelio), healthcare agents (Navina, Hyro, Carefam), Tavily, state-funded rights chat (Kol Zchut), RiseUp, ticket appeals (LoFrayer), exam/study apps, Qodo, D-ID; graveyard LitiGate (IL-001…016) |

## Choices recorded
- IDs `R8-<ISO>-NNN`, numbered per country. Same extra fields as T10/T11: each row's `pl_adaptation_angle` starts with `adapts: <Western product or 'no single leader'>; PL: entered / no / unknown`. **No R8 product was confirmed to have entered Poland.** Wonderful (IL-001) claims 30+ countries; its Polish presence was **not checked** and is the main entry-risk item for T16–T18.
- `works_in_polish`: no product was tried hands-on (time budget); "unknown" for global products, "no" where the product is country-bound (NZ/IL tax, Israeli exam apps) or US-only.
- Companies founded in the country but now selling mainly in the US are filed under the founding country and marked `country_specific = n`: Ivo (NZ), Navina, Hyro, Carefam, Chamelio, Qodo, Tavily (IL), Checkbox (AU, HQ New York).
- State/non-profit products catalogued like Pair (R7) and Bürokratt (R4): NSWEduChat (AU-014), Kol Zchut AI chat (IL-009).
- Product URLs: where a company homepage returned 403 to the fetch tool or its domain could not be confirmed (MiAI Law, Agentsy, Contented, Sterling, Hyro, Carefam, Kol Zchut, RiseUp), the `url` column holds the source article or App Store listing instead.
- Rows with no or unclear LLM core kept for the local pattern, flagged in `llm_role`/`hype_warnings`: APEUni (AU-016), Hnry (NZ-003), Solo (NZ-007), RiseUp (IL-010). That is 4 of 40.
- Weak-traction rows (pre-seed/angel only, or App Store rank with <100 ratings): Isaacus (AU-007), MiAI Law (AU-008), Agentsy (AU-012), RentBetter (AU-013), Sterling (NZ-005), Solo (NZ-007), SortMe (NZ-008), Symphony by Wix (IL-003), LoFrayer (IL-011). That is 9 of 40; T15 should weight them low.
- Out of founder scope but kept as pattern evidence: horizontal infrastructure and dev tools (Relevance AI, Tavily, Qodo), Base44, D-ID (hype marker), RiseUp (would need an AISP licence in PL).

## Poland signal
Like R7, R8 shows **pattern evidence more than entry risk**, with one exception: **Wonderful** (Israel, ~$284M raised in about a year per excerpts) sells local-language customer-service agents country by country with local teams. If it is in Poland or planning to be, a Polish voice/chat agent for enterprises is a contested space; SMB-focused agents (gabinety, warsztaty, przychodnie) are less exposed.

Most important for Poland: **regulated-care and health admin by voice and documents**. Australia funds both clinical scribes (Heidi at 2M+ consults/week; Lyrebird wired into GP EMRs) and NDIS/aged-care paperwork agents (Minikai); Israel exports health call-centre agents (Hyro, 85% calls resolved claimed) and the Maccabi appointment-line agent (Wonderful). Poland has the same pressure points: ageing, carer shortage, and przychodnia phone queues. The Polish adaptation needs gabinet software integrations (KS-SOMED, mMedica), P1/IKP data and NFZ documentation rules; a foreign scribe would struggle with those, not with the language.

Second: **"own the obligation" tax and rights products** for individuals: Hnry (NZ, sole traders: income flows through the service, which pays the tax), Israeli tax-refund services on success fees, Kol Zchut's rights chat. With 삼쩜삼 (R7-KR-001) this is now a 3-region pattern. Polish target: JDG on ryczałt/skala, umowy zlecenie, migrants, with PIT/ZUS/ulgi on Twój e-PIT data.

## Cross-country patterns
1. **Clinical documentation and health front office are the biggest R8 categories**: Heidi, Lyrebird (AU), Navina, Hyro (IL). Heidi's 70% non-AU usage shows a scribe built on one country's GP workflow travels once the EMR layer is rebuilt. Repeats R1 (Abridge), R3 (Nabla notes), R7 (Ubie).
2. **Care-sector compliance agents** (Minikai, NDIS/aged care; Contented's H&S reports): regulation-driven paperwork in care and operations. Repeats R7 NAGARA.
3. **National legal corpora and legal agents**: Lawpath AI (500,000 SME customers, incorporation funnel + Westpac), MiAI Law, Isaacus (AU); Ivo, Chamelio, Checkbox sell to in-house legal globally. The SME layer (Lawpath) is the country-specific one; in-house contract review is already global (Ivo, Chamelio, LegalOn R7).
4. **Tax for accountants and sole traders**: SavvyWise (AU, accountants invest as users), Hnry/Solo (NZ), Israeli success-fee refund services. Same as Blue J (R1), 삼쩜삼 (R7).
5. **Agents bolted onto SME ledgers and HR systems**: Xero JAX (payment follow-ups, document chasing), Employment Hero (payroll anomaly agent), Re-Leased Credia, Sterling. Repeats R7 Bakuraku.
6. **Local-language customer-service agents**: Wonderful (IL), Lorikeet (AU, English). With Born Digital/Linca (R6), WIZ.AI (R7), PolyAI (R2) this is a cross-region theme with a well-funded multi-country player.
7. **Migration and national exams create paid consumer demand**: PTE visa-English apps and citizenship tests (AU top-grossing), Amirnet/psychometric and bar-exam apps (IL). Polish analogue: certyfikat B1 z polskiego for residence/citizenship, matura, egzamin ósmoklasisty.
8. **Consumers pay to fight bureaucracy**: LoFrayer (tickets), settlement finders in the AU Finance chart, Israeli tax-refund apps. Unauthorised-practice-of-law reaction (Israel Bar Association vs LoFrayer) is the key risk.
9. **States build the citizen and student layer** (NSWEduChat, Kol Zchut chat), matching Pair/HKGAI (R7), Bürokratt (R4), BgGPT (R6).
10. **Avatar "digital humans" are the R8 graveyard**: Soul Machines (NZ) in receivership 2026-02, Hour One sold, D-ID consolidating.

## Products also in R0–R7 (spread signal)
Not re-catalogued, seen in R8 charts or sources: **Leonardo.Ai** (R0-AU-013, Australian), **Plaud** (R1; top-30 Productivity in AU, NZ, IL), **Manus** (R0; AU #25, NZ #20, IL #33), **Lovable** (R0; AU #58, NZ #25, IL #29), **Perplexity** (R0; all three), **Praktika** (R2; AU #18, NZ #33, IL #16), **Speak** (R1; AU #27), **Gizmo** (R2; NZ #55), **Owll Translator** (R7-SG-004; IL Business #32), **Loora** (seen in R6/R7 notes; AU #57, NZ #39, IL #5), **Decagon/Sierra** (R0) as the model for Lorikeet and Wonderful. Theme repeats: clinical scribes (Heidi/Lyrebird vs Abridge, Nabla, Ubie), local-language agents (Wonderful vs Born Digital, WIZ.AI), contract review (Ivo/Chamelio vs LegalOn, Spellbook), sole-trader tax (Hnry vs 삼쩜삼, Keeper), state LLMs (NSWEduChat/Kol Zchut vs Pair, Bürokratt).

## Polish adaptation angles from R8 (for T15–T18)
- **Voice/ambient documentation for gabinety POZ and specjaliści** wired into Polish gabinet software and e-recepta/e-skierowanie (Heidi, Lyrebird).
- **Documentation agent for DPS/ZOL, usługi opiekuńcze and asystencja osobista** (Minikai): ageing, carer shortage, audit rules.
- **Voice agent for rejestracja in przychodnie** (Hyro, Wonderful-Maccabi): phone-queue pain; check Wonderful entry.
- **JDG "tax wallet"**: auto-reserve PIT/ZUS/VAT from incoming payments, file JPK_V7 and PIT (Hnry).
- **Rights and benefits assistant** over ZUS, KRUS, MOPS, PFRON, NFZ rules, sold B2B to employers/gminy/NGOs (Kol Zchut).
- **Mandate and parking-fee appeals** (LoFrayer) within legal-information limits (no representation).
- **B1 Polish exam prep with AI speaking scoring for migrants** (PTE apps, citizenship tests).
- **AI tax research on interpretacje indywidualne for biura rachunkowe** (SavvyWise), sold through the accounting community.
- **S24/KRS incorporation + AI-drafted SME documents with a bank partner** (Lawpath + Westpac).

## Coverage

| Country | Status | New rows | R0–R7 overlaps seen | Products researched | Sources read | Searches | Notes |
|---|---|---|---|---|---|---|---|
| Australia | done | 16 | 8 (Leonardo.Ai, Plaud, Manus, Lovable, Perplexity, Praktika, Speak, Loora) | ~32 | 4 pages + 5 feeds | 17 | NDIS search found only Minikai; Startmate/Blackbird/Cut Through not screened |
| New Zealand | done | 8 | 7 (Manus, Lovable, Plaud, Praktika, Gizmo, Perplexity, Heidi/Lyrebird) | ~18 | 1 page + 5 feeds | 9 | small market; 2 weak rows; no NZ vertical LLM champion found |
| Israel | done | 16 | 7 (Plaud, Lovable, Manus, Perplexity, Praktika, Owll, Loora) | ~32 | 2 pages + 5 feeds | 16 (3 Hebrew) | most companies sell in the US; Startup Nation Central blocks bots |
| **R8** | done | **40** | 11 distinct | ~82 | 7 pages + 15 feeds | 42 | |

- Region total **40** is at the 40–80 floor. Reasons it is not higher: New Zealand yields 8 (5M people; AI startups move to the US or are SME-software exporters); Israel's AI capital goes mostly to security and US-market B2B, so Israel-specific LLM products are few; the one-hour budget limited depth; most figures come from search summaries (marked excerpt).
- App Store top-grossing feeds read for all 3 countries × 5 genres (Business 6000, Productivity 6007, Education 6017, Finance 6015, Medical 6020) on 2026-11-01, plus iTunes lookups for ratings, release dates and descriptions. Similarweb Google Play pages, Startmate cohorts, Blackbird portfolio, Cut Through Venture data, Idealog/NBR lists, IVC and Startup Nation Central Finder were **not screened**.
- Durable signals: mostly 1 (replaced spend), 2 (frequent problem), 8 (hard to absorb), 10 (timing). Retention/expansion (signals 3/4): Ivo (ARR x5 in ~11 months, customers x2), Chamelio (revenue x4), Base44 (ARR $59M → ~$100M in a quarter per Wix), Employment Hero (>A$300M ARR claimed, growing >30%), Heidi (2M+ consults/week, 70% abroad), Lawpath (500,000 customers), Re-Leased (1,400 customers since 2011), RiseUp (still top-3 grossing years after launch). No cohort retention or NRR figure found in R8. Hype warnings: Wonderful's rapid valuation step-ups, Base44's free-user inference cost, avatar companies (Soul Machines receivership, D-ID consolidation), one-off exam apps, small-rating chart apps.
- Searched and found nothing: NDIS progress-notes startups beyond Minikai; AI-native accounting firms in AU/NZ/IL; Israeli domestic accounting or HR LLM startups; NZ vertical LLM startups for law, IRD tax, Health NZ or schools; patient-facing generative assistants published by Clalit or Maccabi; any public cohort retention curve.
- Bot-blocked or failed fetches: miai.law, hyro.ai, carefam.com, kolzchut.org.il, riseup.co.il (403 to curl); Wonderful's Maccabi blog page (no article body). Link check 2026-11-01 (R8 files + CSV + countries.md): 287 links, 2 dead fixed (NoCamels RiseUp and LitiGate articles 404, replaced by The Paypers and CodeX TechIndex), then 0 dead. Unverifiable: 4 from R8 (businesswire.com x2, businessnewsaustralia.com, globenewswire.com: 403) + idealog.co.nz (timeout, countries.md) + 8 older non-R8 media links in countries.md (brutkasten.com, datanews.be, startupitalia.eu, timesofmalta.com, netokracija.com, qstp.org.qa, cuti.org.uy, startups.be).
