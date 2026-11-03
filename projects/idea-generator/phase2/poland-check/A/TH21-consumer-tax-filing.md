# TH21 — Consumer tax filing (Poland check)

Theme: [THEMES.md#th21](../../themes/THEMES.md#th21) · rank 17, batch A · sources accessed **2026-11-03** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| **Twój e-PIT** (KAS, state) | Pre-filled PIT-37/38/36/28 returns, auto-accepted on 30 April | free | record 14.8 million documents for tax year 2025 (8.9 million accepted by taxpayers, 5.9 million auto-accepted) | [podatki.biz](https://www.podatki.biz/artykuly/pit-za-2025-rok-148-mln-podatnikow-wybralo-twoj-e-pit_16_62231.htm) |
| PITax | Online PIT program; question-driven ulgi suggestions, UPO, expert chat/phone, audit support for 5 years; no AI mentioned | free (funded by 1.5% OPP and upsells) | site claims 12 million users | [pitax.pl](https://www.pitax.pl/) |
| e-pity, Program PIT, Pitbot | Free PIT programs and apps | free | not stated | [e-pity.pl](https://www.e-pity.pl/); [programpit.pl](https://www.programpit.pl/); [pitbot.pl](https://pitbot.pl/) |
| **Euro-Tax.pl S.A.** (Wrocław) | Done-for-you **foreign** tax refunds (DE, NL, UK, BE, AT), app and client panel, child-benefit claims abroad; no AI mentioned | fee after success (amount not published) | 550k clients, 999 million PLN recovered, average refund 3,252–4,087 PLN; BG/RO/UA versions | [euro-tax.com](https://euro-tax.com/) |
| PIT-38 tools for foreign brokers: kloPIT (free, open source, IBKR), `pit-38` CLI (PyPI), PIT Inwestora (Product Hunt launch) | Compute PIT-38/PIT-ZG from IBKR and other broker statements | free / not stated | retail investors; Wykop discussion of kloPIT | [PyPI pit-38](https://pypi.org/project/pit-38/); [Product Hunt](https://www.producthunt.com/products/pit-inwestora); [freenance.io guide](https://freenance.io/podatki/pit-38-zagraniczny-broker-2026-ibkr-trading-212-etoro-jak-rozliczyc-krok-po-kroku/) |
| Free calculators and SEO guides (sum.money, freenance.io) | PIT/ZG guides for income from DE/UK/NL | free | — | [freenance.io](https://freenance.io/podatki/pit-zagraniczne-dochody-2026-pit-zg-niemcy-uk-rozliczenie-jak-zlozyc/) |

## 2. Does the Western leader already serve Poland?
- **Taxfix** (DE): German, Italian and Spanish markets; site in English/German; files German returns only. Relevant only to Poles who worked in Germany. **Not a Polish-return product.** ([taxfix.de/en](https://taxfix.de/en/))
- **Samjjeomsam** (KR), **TaxDown** (ES), **Heru** (MX): national-system only; not in PL.
- Could not check: Taxfix's flow for non-resident filers (requires account).

## 3. Polish demand signals
- Autocomplete: "zwrot podatku" → "… z niemiec", "… na dziecko"; "ulga na dziecko" → "… 2026 limit dochodu", "… pełnoletnie"; "pit zagraniczny" → "… niemcy jak rozliczyć", "… holandia", "pit 38 zagraniczny broker"; "pit 36 zg" → "… jak wypełnić", "… niemcy wzór wypełniony", "… norwegia"; "rozliczenie pit z holandii" → "… cena", "… online"; **"pit dla ukraińca" → "pit 11 dla ukraińca jaki urząd skarbowy", "rozliczenie pit dla ukraińca", "pit 11 czy ift dla ukraińca"**; "rozliczenie najmu ryczałt" → "… jaki pit".
- Search demand concentrates on **foreign income**, **foreign brokers** (PIT-38 with IBKR/eToro, "pit 8c zagraniczny broker") and **Ukrainian taxpayers**, the cases Twój e-PIT does not pre-fill.

## 4. What adaptation needs
M03 e-Deklaracje/e-Urząd Skarbowy submission, M18 Profil Zaufany/M19 mObywatel login (Twój e-PIT), PIT/ZG and double-tax treaty methods per country, PIT-38 from foreign broker statements (currency conversion at NBP rate D-1), ulga na dziecko and residency rules (IFT-1R vs PIT-11 for foreigners), M32 BLIK payment. Liability: tax advice is regulated (doradca podatkowy), but self-filing software is not.

## 5. Demographic or social driver
DD6: 1.29 million foreigners insured in ZUS (D33), mostly Ukrainians who receive PIT-11 and are confused about residency; D36: 1.5 million Poles abroad, many with foreign income or returning; DD12 rising incomes bring more retail investors with foreign brokers (not quantified here).

## 6. CEE check
No CZ/SK/RO/HU consumer tax app in R6 ([R6 catalogue](../../catalogue/R6-cee-peers.csv)); Euro-Tax itself expands from PL to BG/RO/UA.

## 7. Verdict: **partial**
Domestic returns are taken by the free state pre-fill (Twój e-PIT) and free programs with millions of users, so a Samjjeomsam clone has no refund gap to sell. Foreign refunds are served by Euro-Tax without AI. The residue is complex cases the state does not pre-fill: foreign brokers (already crowded with free tools such as kloPIT and PIT Inwestora) and foreigners filing in Poland, where search demand is visible and no product in Ukrainian was found.

**Seed idea:** UA/EN/RU **PIT assistant for foreign employees in Poland**: reads PIT-11 photos, decides residency (PIT-37 vs IFT-1R case), applies ulga na dziecko and joint filing, explains in Ukrainian, then hands the user a pre-checked return for Twój e-PIT; per-filing price (e.g. 39–59 PLN) or B2B via employers and staffing agencies as a benefit. (A broker PIT-38 tool is a weaker alternative: free competitors exist.)
