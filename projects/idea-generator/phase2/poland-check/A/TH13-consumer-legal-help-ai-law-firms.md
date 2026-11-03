# TH13 — Consumer legal help and AI-enabled law firms (Poland check)

Theme: [THEMES.md#th13](../../themes/THEMES.md#th13) · rank 22, batch A · sources accessed **2026-11-03** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| **mObywatel virtual assistant** (state, PLLuM model) | Answers questions about public services since 2025-12-31; does not interpret law or replace advice | free | mObywatel users | [podatki.biz](https://www.podatki.biz/artykuly/nowa-usluga-w-mobywatelu-wirtualny-asystent_16_60816.htm) |
| **Nieodpłatna pomoc prawna** (state, per powiat) | 1,490 free legal-aid points in 2024, three fewer in 2025, funded by state grants to powiaty; consultation counts not found | free | eligible residents | [prawo.pl](https://www.prawo.pl/samorzad/dotacja-na-nieodplatna-pomoc-prawna-a-oczekiwania-powiatow,528048.html) |
| Zapytaj Kodeks | Free AI legal-information Q&A with sources, beta, launched via a Wykop post (2024-07) | free | not stated | [android.com.pl](https://android.com.pl/tech/778215-zapytaj-kodeks-program-ai/) |
| e-prawnik.pl and online legal-advice firms | Paid human online advice and letters (e.g. ZUS appeals) | per case (not checked) | consumers | [e-prawnik.pl](https://e-prawnik.pl/uslugi-prawne/pomoc-zus.html) |
| ChatGPT and other assistants | Citizens send AI-drafted complaints and appeals to offices, sometimes with prompts left in; NSA criticised unverified AI in court filings (I FZ 104/26, 2026-06-23) | free / 20 USD | general public | [spidersweb.pl](https://spidersweb.pl/2026/08/prompt-w-pismie-urzedowym-chatgpt.html); [infor.pl](https://www.infor.pl/prawo/nowosci-prawne/7623766,ai-w-pismach-procesowych-do-sadu-halucynacje-postanowienie-nsa-2026.html) |
No Polish consumer AI legal product with visible traction (paying users, funding, app rank) was found in three Polish searches.

## 2. Does the Western leader already serve Poland?
- **Lawhive** (UK, AI-enabled law firm), **Valla** (UK, employment), **LoFrayer** (IL), **Mohami/Legaline** (Gulf): each tied to its jurisdiction and bar rules; no Polish site found. **Not in PL.**
- **Lawren.ai / AI+ Avocat** (RO): Romanian law only.
- Could not check: Lawhive signup flow (UK postcodes required).

## 3. Polish demand signals
- Autocomplete: "porada prawna online" → "… za darmo", "… prawo pracy", "… za darmo czat", "… cena", "… prawo rodzinne", "… 24h", "… prawo spadkowe"; "odwołanie od mandatu" → "… mpk wrocław", "… za parkowanie", "… wzór", "… za brak biletu wzór", "… karnego". **High-intent, document-shaped demand** (templates for transit fines, parking, employment, inheritance).
- Citizens already use ChatGPT for letters to offices (spidersweb above).

## 4. What adaptation needs
M52 Polish legal language and forms; M31 ISAP/ELI for current law text, M29 SAOS and M30 court rulings for citations; procedures: e-Sąd/EPU sprzeciw od nakazu zapłaty, odwołanie od decyzji ZUS (M07), opłata dodatkowa in public transport (uchwały per city), parking-zone fines (strefa płatnego parkowania per gmina); M18 Profil Zaufany/M17 ePUAP for e-filing. Regulation: advice outside court is not reserved to adwokaci/radcy in Poland (theme note: lower unauthorised-practice risk than IL/UK), but court representation is; consumer protection (UOKiK) for paid templates.

## 5. Demographic or social driver
DD6 foreigners facing Polish offices and employers (UA/EN demand), DD1 seniors with ZUS and inheritance matters, DD12 rising incomes and service prices make a 300–500 PLN lawyer consultation feel expensive vs. a 30 PLN letter.

## 6. CEE check
Romania has two consumer legal-AI launches (Lawren.ai backed by a law firm, AI+ Avocat with lawyer validation) per [R6 README](../../research/regions/R6-cee-peers/README.md); neither shows plans for Poland.

## 7. Verdict: **partial**
The free state options (legal-aid points, mObywatel assistant) and ChatGPT cover general questions, but no Polish product turns a specific dispute into a correct, current, fileable document, while search demand for exactly that ("wzór", "za darmo", per-city fines) is strong. Free substitutes and ChatGPT cap prices, so the product must win on correctness per procedure and on local data (per-city uchwały, current forms).

**Seed idea:** per-procedure letter engine, starting with **public-transport and parking fines** (opłata dodatkowa MPK/ZTM, strefa płatnego parkowania): user photographs the wezwanie, the agent checks the city's uchwała and deadlines, and outputs a reklamacja/odwołanie with citations; 19–29 PLN per letter, then extend to sprzeciw od nakazu zapłaty (EPU) and ZUS appeals.
