# TH59 — Citizen and SME public-service navigators (Poland check)

Theme: [THEMES.md#th59](../../themes/THEMES.md#th59) · rank 25, batch B · sources accessed **2026-11-04** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| mObywatel virtual assistant (state, PLLuM + RAG) | Live since 2025-12-31; navigates the app, answers questions about its services, points to forms and applications | free | mObywatel has 10M+ users; assistant usage figures not published | [imagazine.pl 2026-01-02](https://imagazine.pl/2026/01/02/mobywatel-wchodzi-w-2026-rok-z-polskim-ai/); [purepc.pl](https://www.purepc.pl/mobywatel-asystent-ai-pllum-rag-chatbot-sprawy-urzedowe-ulatwienie) |
| ZUS | AI used internally only (ticket classification); a client chatbot/voicebot is "potential", not deployed (communiqué 2026-02-18) | — | — | [infor.pl 2026-02](https://www.infor.pl/prawo/nowosci-prawne/7523836,sztuczna-inteligencja-pomaga-zus-w-pracy-w-ktorych-systemach-zus-juz-jest-ai-a.html) |
| Right to Protection "Legal Adviser 2.0" (NGO) | Free Telegram bot for Ukrainians on legalisation and paperwork, escalates to human experts; since 2024-03 | free | not stated | [r2p.org.ua](https://r2p.org.ua/page/legal-adviser-20-for-ukrainians-in-poland-chatbot-is-launched) |
| Legalisation agencies and law firms | Human service for residence and work permits | average 4,457 PLN per person in 2026 (price aggregator, excludes fees and translations) | foreigners and employers | [cenauslug.pl](https://cenauslug.pl/firma-i-biuro/legalizacja-pobytu-i-zatrudnienia-cudzoziemcow) |
| jakiwniosek.pl | Directory of official forms per gmina/starostwo (wzory PDF, online links); no AI | free (ads) | not stated | [jakiwniosek.pl example](https://jakiwniosek.pl/wnioski/nieruchomosci/wypis-i-wyrys-z-ewidencji-gruntow-i-budynkow/zawiercie) |

The general "what am I entitled to / which form" question is being absorbed by the state (mObywatel assistant) and by ChatGPT. The paid residue is **foreigners' legalisation**, where human intermediaries charge thousands of PLN.

## 2. Does the Western leader already serve Poland?
- **Kol Zchut** (IL), **Bürokratt** (EE), **mAigov** (GR), **TAMM** (AE) are state or NGO services tied to their own country's law; not exportable products. **EffiGov** (US) sells to US agencies (B2G). **Issa** (BH) is a chamber-of-commerce bot. None operates in PL.
- Could not check: none of these has a signup flow relevant to Poland.

## 3. Polish demand signals
- Autocomplete (2026-11-04): "mos wniosek" → 8 suggestions (pobyt czasowy, karta pobytu, pobyt stały, **cukr**, rezydent długoterminowy, dla dziecka); "mos cudzoziemcy" → 10 incl. "logowanie", "rejestracja", "infolinia", "**nie działa**"; "karta cukr" → 10 incl. "warunki", "dokumenty", "opłaty", "od kiedy"; "jaki wniosek złożyć" → 10, mostly ZUS (przeliczenie emerytury, grupa inwalidzka, wakacje od ZUS) and PFRON; "dofinansowanie dla firm 2026" → 10 variants; "jakie świadczenia mi przysługują" → none.
- Press: from **2026-04-27** residence applications can be filed **only** through MOS 2.0 with login.gov.pl and an e-signature, employer must co-sign; CUKR applications for people under temporary protection opened 2026-05-04; 900k+ beneficiaries, ~800k CUKR applications expected; backlogs of 38,000+ cases in one office and up to three-year waits in Lower Silesia; missing the deadline means illegal stay and employer fines of 3,000–50,000 PLN ([ceo.com.pl](https://ceo.com.pl/en/?p=5085)). Earlier OKO.press reporting quotes an intermediary saying only intermediaries keep up with the system ([OKO.press](https://oko.press/chaos-cyfryzacja-wnioskow-o-legalizacje-pobytu-cudzoziemcy)).

## 4. What adaptation needs
M18 login.gov.pl / Profil Zaufany, M17 ePUAP, M19 mObywatel, M07 ZUS PUE (for ZUS navigators), M08 praca.gov.pl, MOS 2.0 portal flow and form fields, Ustawa o cudzoziemcach and specustawa ukraińska (TPD until 2027-03-04), urzędy wojewódzkie practice per voivodeship, translation into UA/RU/EN. The applicant must sign himself, so a product can prepare and check, not file on someone's behalf without a pełnomocnictwo.

## 5. Demographic or social driver
DD6: 1.56M Ukrainians with valid permits and 1.29M foreigners in ZUS; the CUKR transition creates a one-off wave of ~800k applications in 2026–27, then recurring renewals. DD5/DD1 drive ZUS pension and disability questions for citizens.

## 6. CEE check
No CZ/SK/RO/HU navigator in R6 ([R6 catalogue](../../catalogue/R6-cee-peers.csv)).

## 7. Verdict: **partial**
The citizen-wide navigator is taken by the state (mObywatel PLLuM assistant, free) and by general assistants. Foreigners facing the MOS 2.0 / CUKR switch are poorly served: a free NGO bot and human agencies at ~4.5k PLN, with no product that prepares a correct MOS application in Ukrainian. Overlaps with the employer-side TH34 seed ("Legalny pracownik") in batch A; the two should be merged in T19.

**Seed idea:** "MOS bez stresu": UA/RU/EN assistant that interviews the foreigner, picks the right permit type (CUKR, pobyt czasowy, stały), lists documents, pre-checks scans, writes the uzasadnienie and walks through MOS 2.0 step by step, including the employer's part; 99–199 PLN per application, sold through employers and staffing agencies as a bulk package.
