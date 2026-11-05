# TH11 — Plaintiff litigation casework (Poland check)

Theme: [THEMES.md#th11](../../themes/THEMES.md#th11) · rank 45, batch B · sources accessed **2026-11-05** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Votum S.A. (listed) | Largest claimant-side firm: compensation claims and CHF-loan (frankowe) cases | success fees (not checked) | Q1 2026 consolidated revenue 105.6 PLN M vs 123.1 PLN M a year earlier (−14%), which DM BOŚ attributes to normalisation of CHF cases after a record 2025 | [bankier.pl Q1 2026 report](https://www.bankier.pl/wiadomosc/VOTUM-S-A-Wyniki-finansowe-QSr-1-2026-9141854.html); [DM BOŚ 2026-06-17](https://www.biznesradar.pl/storage/a/vo/t-/vot-2026-06-17-bos-54bcba4.pdf) |
| Gaius-Lex (Kraków, 2024) | Polish legal AI: research of statutes and case law, document analysis, contract risk review, drafting, anonymisation | not found | Polish law firms (count not found) | [Stanford CodeX techindex](https://techindex.law.stanford.edu/companies/gaius-lex) |
| LEX Expert AI (Wolters Kluwer) | Chat over LEX acts, judgments and commentaries with source links; WK says it can list what a pleading typically needs but is not meant to produce templates | LEX subscription (standalone price not found) | LEX subscribers | [wolterskluwer.com](https://www.wolterskluwer.com/pl-pl/solutions/lex/expert-ai/dlaczego-lex-expert-ai) |
| Kancelarie odszkodowawcze and frankowe | Hundreds of local firms (city-level searches below) | success fee | individuals | autocomplete |

No Polish product was found that builds **medical chronologies** or **demand packages** (wezwanie do zapłaty / pozew with damages calculation) from a client's medical and accident file.

## 2. Does the Western leader already serve Poland?
- **EvenUp**, **Eve**, **Supio** (US): built for US personal-injury practice (demand letters to US insurers, US medical billing codes, contingency fee economics); English only; no EU presence found (theme record; sites not re-opened).
- **Turbo Law** (TR): Turkish litigation platform, 1,800+ active case files (company claim); Turkish law only ([Global Legal Post](https://www.globallegalpost.com/news/us-ai-litigation-platform-start-up-turbo-law-raises-38m-in-pre-seed-funding-round-1445015597)).
- Generic medical-record summarisers (Medrecords AI, Brighterway, Wisedocs) target US/UK/CA claims ([legaltechnologyhub](https://www.legaltechnologyhub.com/vendors/medrecords-ai/)). **Not in PL.**

## 3. Polish demand signals
- Autocomplete (2026-11-05): "odszkodowanie za wypadek" → 10 (w pracy, ZUS, w drodze do pracy, komunikacyjny, z OC sprawcy); "zadośćuczynienie za" → 10 (doznaną krzywdę, wyciek danych osobowych, naruszenie dóbr osobistych, stres); "kancelaria odszkodowawcza" → 10 (8 cities, "ile bierze", "praca"); "pozew o zadośćuczynienie" → 10 ("wzór", "właściwość sądu", "opłata", "mobbing"); "błąd medyczny odszkodowanie" → 2; "ai pismo procesowe" → empty. Consumer demand is large and local; firm-side AI search is nil.
- CHF litigation, the biggest claimant-side volume, is falling: some courts report up to 60% fewer new suits y/y in early 2026 ([podatki.biz](https://www.podatki.biz/artykuly/sprawy-frankowe-spadek-liczby-pozwow-i-poprawa-efektywnosci-sadow_16_58880.htm); [infor.pl 2024](https://www.infor.pl/prawo/nowosci-prawne/6668431,mniej-nowych-pozwow-frankowiczow-w-sadach-w-2024-roku-co-sie-stalo-banki-poprawily-warunki-ugod.html)).

## 4. What adaptation needs
- Polish damages law: zadośćuczynienie (art. 445/446 kc), OC sprawcy claims handled first with insurers, ZUS jednorazowe odszkodowanie for work accidents, Rzecznik Finansowy route; amounts benchmarked against court practice, which can be mined from SAOS and Portal Orzeczeń (M29, M30) and statutes from ISAP (M31).
- Polish medical records (EDM, IKP exports, M23–M24) and Polish medical terminology; health data are special-category data under RODO art. 9, so hosting and DPA terms matter.
- Pleading conventions and forms (M52); e-filing via Portal Informacyjny.

## 5. Demographic or social driver
DD1/DD3: an ageing population and long NFZ queues (D19) feed medical-malpractice and accident claims; no direct numeric driver for claim volumes was found.

## 6. CEE check
No CZ/SK/RO/HU product in the [R6 catalogue](../../catalogue/R6-cee-peers.csv). Turkish and US leaders are law-bound and unlikely to enter.

## 7. Verdict: **partial**
Generic Polish legal AI (Gaius-Lex, LEX Expert AI) covers research and drafting, but nobody does the EvenUp job of turning a Polish injury file (medical records, police notes, insurer decisions) into a chronology and a claim with an amount justified by Polish case law. The market is smaller and cheaper than US PI: claims settle mostly with insurers, amounts are lower, and the CHF wave that funds the largest firms is shrinking.

**Seed idea:** claim-file assistant for kancelarie odszkodowawcze: upload medical and accident documents, get a dated medical chronology, a list of missing documents, and a zadośćuczynienie range with similar SAOS judgments, plus a draft wezwanie do zapłaty to the OC insurer; 30–60 PLN per case or 399–899 PLN/month per firm. RODO art. 9 hosting in the EU from day one.
