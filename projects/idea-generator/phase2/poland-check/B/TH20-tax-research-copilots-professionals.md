# TH20 — Tax research copilots for professionals (Poland check)

Theme: [THEMES.md#th20](../../themes/THEMES.md#th20) · rank 31, batch B · sources accessed **2026-11-04** · method: [README](README.md#method).

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Wolters Kluwer LEX Expert AI | Generative chat inside LEX answering from verified LEX content with cited legal basis; July 2026 release targets non-lawyers incl. accounting/tax staff and tax advisory offices; closed environment | LEX subscription (not checked) | LEX user base | [Wolters Kluwer PL 2026-07-14](https://www.wolterskluwer.com/pl-pl/news/lex-expert-ai-wspiera-specjalistow-ktorzy-nie-sa-prawnikami) |
| LEX Kompas Interpretacje Podatkowe | AI tool for working through interpretacje podatkowe held in LEX (launched 2025-01) | add-on (not checked) | tax specialists | [Wolters Kluwer PL 2025-01-23](https://www.wolterskluwer.com/pl-pl/news/wolters-kluwer-polska-dostarcza-nowe-narzedzia-specjalistom-pracujacym-z-interpretacjami-podatkowymi) |
| Beck-Noxtua (Legalis), INFOR, Gaius-Lex | Legal-research AI on Polish law found in batch A ([TH07](../A/TH07-legal-research-national-law.md)); tax is part of the same corpora | subscriptions | law and tax firms | batch A TH07 |
| State: EUREKA (KIS) | Free official search of individual interpretations | free | everyone | autocomplete below |
| Training market | Courses on using ChatGPT/Copilot for tax work, warning of invented KIS interpretations and court rulings and the adviser's liability | per course | accountants, advisers | [podatki.biz course 2026-08-06](https://www.podatki.biz/artykuly/[06-08-2026]-szkolenie-on-line-jak-wykorzystac-ai-chatgpt-copilot-w-rozliczaniu-podatkow-zalety-ryzyka-i-kontrola-poprawnosci_38_61774.htm) |

## 2. Does the Western leader already serve Poland?
- **Blue J** (CA): US, Canadian and UK tax content; no Polish law (theme row, not re-checked). **Not in PL.**
- **Nexana.ai** (SK): best coverage SK/CZ law; **Polish law listed as supported** in the FAQ (depth unknown); SK/CZ/EN interface only; 23.20–159.20 EUR/month, 7-day free PRO trial without a card ([nexana.ai](https://www.nexana.ai/)). **Nominally in PL**, not localised.
- **TaxGPT** (US), **SavvyWise** (AU), **Leapifai** (IE): home-market tax law.
- Could not check: Nexana's answer quality on a Polish VAT question (trial not started; no account creation).

## 3. Polish demand signals
- Autocomplete (2026-11-04): "interpretacje podatkowe wyszukiwarka" → 4 incl. "gov", "kis"; "eureka interpretacje" → 3; "ai podatki", "asystent podatkowy ai" → echo only; "chat gpt podatki" → "chatgpt podatki". Professionals use the free state database and ChatGPT; little branded search for AI tax tools.
- Deregulation package "Deregulacja 2.0" (2026-07-06) proposes five-year validity for interpretations (INFOR report, details not read).

## 4. What adaptation needs
M05 EUREKA interpretations (no API, scraping), objaśnienia podatkowe MF, M29 SAOS / CBOSA for NSA/WSA rulings, M31 ISAP/ELI for act versions in force on a date, M01 KSeF and M02 JPK rules, Polish tax language. The corpus is public, so the moat is curation and citation reliability, which publishers already sell.

## 5. Demographic or social driver
None specific. DD7 labour shortage in accounting offices (not quantified here) pushes productivity tools.

## 6. CEE check
Nexana.ai (SK) lists Polish law and sells self-serve in EUR; it could add a Polish interface cheaply ([R6 catalogue](../../catalogue/R6-cee-peers.csv) `R6-SK-001`).

## 7. Verdict: **taken**
Wolters Kluwer already ships AI over Polish tax interpretations (2025) and a chat for tax staff (2026), Beck and INFOR cover the same buyers, and Nexana (SK) lists Polish law. Professionals who don't pay for LEX use free EUREKA plus ChatGPT. No definable segment left that a solo founder could own.

**Seed idea (residue, weak):** citation checker for accountants: paste a ChatGPT tax answer, the tool verifies every cited interpretation signature and ruling against EUREKA/CBOSA and flags invented or outdated ones; cheap, but a feature for LEX/Beck.
