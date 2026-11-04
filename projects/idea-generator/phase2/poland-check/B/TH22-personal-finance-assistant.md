# TH22 — Personal finance assistant (Poland check)

Theme: [THEMES.md#th22](../../themes/THEMES.md#th22) · rank 35, batch B · sources accessed **2026-11-04** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Bank apps (PKO BP IKO, mBank, ING, Credit Agricole) | In-app spending analysis by category; PKO's IKO voice assistant has analysed spending and savings since 2021-09 and later added transfers and ATM withdrawals; mBank AI assistant announced for 2026 (press, not confirmed by the bank) | free to account holders | PKO: over 460k analyses requested by 2024-01 (bank press office) | [bank.pl 2021](https://bank.pl/?p=383493); [bank.pl 2024-01](https://bank.pl/bankowosc-i-finanse-technologie-w-smartfonach-zagniezdzil-sie-finansowy-pomocnik/); [bezprawnik on mBank](https://bezprawnik.pl/asysten-ai-w-mbanku/) |
| Freenance ("Made in Poland") | Web PFM: MT940/CSV import or PSD2 sync via Synci.io (mBank, ING, PKO BP, Revolut, Credit Agricole, Millennium, Nest named), Gemini auto-categorisation with account numbers stripped, "Axe" AI assistant answering from the user's data, Polish Treasury bonds | USD 99.99–299.99/year (PLN amounts not shown); 14-day trial | not published; operating company not named on the site | [freenance.io](https://freenance.io/) |
| Wallet by BudgetBakers (CZ), Spendee | Budgeting apps with PSD2 bank sync as a paid premium feature, widely used in CEE | premium about 12.99 PLN/month (competitor-reported, unverified) | not checked | [BudgetBakers Wallet](https://budgetbakers.com/en/products/wallet/); [Freenance comparison (competitor)](https://freenance.io/porownania/freenance-vs-wallet-budgetbakers/) |
| Kontomierz | Long-standing Polish PFM with automatic tracking; current status not verified | not checked | not checked | [packagist client (2026-05)](https://root.packagist.org/packages/woojos/kontomierz) |

Plus ChatGPT, which users can feed a bank CSV for free.

## 2. Does the Western leader already serve Poland?
- **Cleo** (US/UK): a Cleo job posting found by search said the app cannot be downloaded in Poland (the posting is now 404, so this is unverified as of today); the website returned 403 to the fetcher. **Not in PL as far as can be checked.**
- **RiseUp** (IL): Israeli bank integrations only. **Not in PL.**
- **Dovly AI** (US): credit-repair against US bureaus. The Polish analogue would sit on BIK reports. **Not in PL.**
- **Bilance** (EE), **Finno** (MX), **Kebo** (CO): home-market.
- Could not check: Cleo app-store availability by country (no account, no Polish store login).

## 3. Polish demand signals
- Autocomplete (2026-11-04): "aplikacja do budżetu domowego" → 10 (darmowa, dla par, po polsku, iphone, excel); "aplikacja do oszczędzania" → 9; "asystent finansowy ai" and "kontrola wydatków aplikacja" → echo only.
- Debt pain is strong: "jak wyjść z długów" → 10 (chwilówek, u komornika, w parabankach, forum, bez zdolności kredytowej); "raport bik" → 10 (za darmo, cena, mobywatel, 2026).
- Search results for budgeting apps are dominated by one vendor's (Freenance) SEO pages, which shows the niche is small enough for a single player to own the SERP.

## 4. What adaptation needs
PSD2 access to Polish banks: own access needs a KNF AIS registration, or a licensed aggregator (Synci.io and similar) as Freenance does; M32 BLIK for subscriptions; Polish bank CSV/MT940 formats; BIK reports (paid, available via mObywatel per autocomplete); Polish Treasury bonds and PPK (M06) for savings views. Investment or credit advice needs a licence (brief: out of scope), and credit intermediation needs KNF registration.

## 5. Demographic or social driver
DD12: incomes ×2.5 in ten years, rising discretionary spend. DD5: shrinking replacement rates push saving. Debt stress (chwilówki, komornik searches) is a social driver, but those users have low willingness to pay.

## 6. CEE check
BudgetBakers Wallet and Spendee (CEE origin) already serve Polish users with bank sync; Bilance (EE) is in R4, not R6. No AI-coaching PFM from R6 in the [R6 catalogue](../../catalogue/R6-cee-peers.csv).

## 7. Verdict: **taken**
Spending analysis is free inside the dominant bank apps, CEE budgeting apps sync Polish banks, and a Polish AI-assistant PFM (Freenance) already exists; B2C willingness to pay for budgeting is low and advice-like features hit licensing. The leaders abroad (Cleo, RiseUp) lean on cash-advance or bank-specific features that would need a lending or AIS licence in Poland.

**Seed idea (weak, residue only):** a BIK report and debt-pile explainer for over-indebted households: upload the BIK PDF and komornik letters, get a plain-Polish map of creditors, deadlines and legal options (upadłość konsumencka, ugoda), with referral to licensed advisers; 29–49 PLN one-off. Education only, no credit advice.
