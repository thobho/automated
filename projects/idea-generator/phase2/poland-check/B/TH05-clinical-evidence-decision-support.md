# TH05 — Clinical evidence and decision support (Poland check)

Theme: [THEMES.md#th05](../../themes/THEMES.md#th05) · rank 29, batch B · sources accessed **2026-11-04** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Mediately (SI) — Polish edition | Polish drug database from RPL and MZ data, ICD codes, interaction checker; PRO tier adds renal/hepatic/paediatric dosing; no AI assistant found | free + PRO (price not checked) | 620,000+ healthcare workers in 12 countries | [mediately.co/pl](https://mediately.co/pl) |
| PWN/PZWL "MEDICO" assistant with MediChat | AI answers clinical questions with cited sources from 150,000+ licensed documents (journals, guidelines, PZWL/PWN books), drug and interaction database, calculators; for POZ doctors, specialists, residents, students | not stated | not stated (article 2025-06-03) | [android.com.pl](https://android.com.pl/tech/935156-inteligentny-asystent-medyczny-pwn/) |
| Medycyna Praktyczna (mp.pl) | Polish guidelines and drug content publisher; no AI assistant found in one search | subscription | doctors | [mp.pl article on AI](https://www.mp.pl/pacjent/aktualnosci/397861,ai-czas-by-sie-obudzic) |
| Global publishers (UpToDate, ClinicalKey AI, BMJ Best Practice) | English evidence tools with AI layers, institutional licences | institutional | hospitals, universities | named in [wwwhatsnew.com](https://wwwhatsnew.com/?p=491657) |

## 2. Does the Western leader already serve Poland?
- **OpenEvidence** (US): **withdrew from the EU and UK on 2026-04-30**, citing European regulatory uncertainty; the article links it to the AI Act treating clinical decision support as high-risk from 2026-08-02 ([wwwhatsnew.com](https://wwwhatsnew.com/?p=491657)). Access also requires NPI verification for full use (secondary source). **Not available in PL.**
- **Navina** (IL) is sold to US primary-care groups; **Eolas** (UK) to NHS trusts; **EvidenceMD** (MX) home market. **PMcardio** (SK) is a CE-marked ECG AI sold in the EU, a device product rather than an evidence assistant.
- Could not check: OpenEvidence's own EU notice (site geo-blocked statement reported, not read directly).

## 3. Polish demand signals
- Autocomplete (2026-11-04): "ai dla lekarzy" → 9 incl. "aplikacja", "chat", "asystent", "kurs", "**pzwl ai dla lekarzy**", "najlepsze", "**openevidence ai dla lekarzy**", "szkolenia"; "openevidence" → 10 incl. "**europe**", "alternative", "login"; "asystent ai dla lekarza" and "chpl leku" → echo only.
- Polish doctors know and search for OpenEvidence and alternatives, and PZWL is already the branded local answer.

## 4. What adaptation needs
Polish ChPL drug labels (RPL), refund lists (obwieszczenia refundacyjne MZ), Polish society guidelines (PTK, PTD, PTL etc.), NFZ coverage rules, M24 P1 e-recepta context, Polish medical language. Regulation dominates: a tool that suggests diagnosis or treatment is likely a medical device under MDR (class IIa+) and high-risk under the AI Act; the founder profile excludes medical licensing and heavy compliance.

## 5. Demographic or social driver
DD3: specialist waits of 4.2–4.3 months and doctors on the shortage list push more decisions onto POZ doctors, raising demand for quick reference; DD1 ageing increases polypharmacy.

## 6. CEE check
Mediately (SI) already serves Poland in Polish; PMcardio (SK) sells EU-wide ([R6 catalogue](../../catalogue/R6-cee-peers.csv) `R6-SI-004`, `R6-SK-003`).

## 7. Verdict: **taken**
The Polish evidence/drug-reference niche is held by Mediately (Polish drug data) and PZWL/PWN's MEDICO with an AI assistant on licensed Polish content, and global publishers serve hospitals. OpenEvidence's EU exit opens space, but the space is high-risk under the AI Act and MDR, which rules it out for a solo founder without a medical-device budget.

**Seed idea (residue, weak, regulated):** non-diagnostic "refundacja + ChPL" lookup for pharmacists and POZ (which indication is refunded, at what level, under which obwieszczenie), staying informational to avoid device status; needs a regulatory opinion first.
