# TH10 — Law-practice operations and AI secretariat (Poland check)

Theme: [THEMES.md#th10](../../themes/THEMES.md#th10) · rank 21, batch A · sources accessed **2026-11-03** · method: [README](README.md#method). Legal research itself is covered in [TH07](TH07-legal-research-national-law.md) (taken); this file covers intake, phone, case files and chores for small firms.

## 1. Polish players
| Product | What | Price | Customers | Source |
|---|---|---|---|---|
| Wolters Kluwer **LEX Kancelaria Prawna / Prawnik360** | Practice-management software (cases, deadlines, time, invoicing) tied to LEX | not published (page bot-blocked) | Polish firms | [Wolters Kluwer PL](https://www.wolterskluwer.com/pl-pl/solutions/lex/oprogramowanie-dla-kancelarii) |
| ≥30 practice-management programs in Poland | KIRP-backed report counted at least 30; boxed vs custom discussed by prawo.pl | various | radcy and adwokaci | [prawo.pl](https://www.prawo.pl/prawnicy-sady/aplikacja-dedykowana-czy-z-pudelka,170760.html) |
| VOLARIA AI S.A., **VAI Legal** | AI legal-document analysis platform; commercialisation from 2026-03-31, strategic cooperation agreement 2026-05 | not stated | not stated | [Parkiet ESPI](https://www.parkiet.com/komunikaty-espi/art44424271-volaria-ai-spolka-akcyjna-zawarcie-umowy-o-wspolpracy-strategicznej-w-ramach-projektu-vai-legal) |
| Advocly (Warsaw) | AI contract analysis; 50k EUR raised (Dealroom, 2025-04) | not stated | not stated | [Dealroom](https://app.dealroom.co/companies/advocly) |
| Generic voice receptionists (see TH26) | Phone answering at 169–499 PLN/month | | SMEs incl. firms | [TH26](TH26-ai-receptionist-smes.md) |
No Polish product found that does **intake + court-portal monitoring + deadline calculation + first drafts** for small firms in one workflow (one Polish search).

## 2. Does the Western leader already serve Poland?
- **JUPUS** (DE): German-only; "over 2,000 lawyers in Germany", BRAO/§203 StGB compliance; KI-Sekretariat 97 EUR/user/month + 149 EUR platform fee, phone AI "Marie" +99 EUR/month ([jupus.de](https://www.jupus.de/)). **Not in PL.**
- **Clio** (CA): Polish-path page returned 403 to the checker; no Polish court integration or PLN pricing found. **Not adapted.**
- **Lemontech** (CL), **Safahat.ai** (TR), **LawX** (DE): home markets only.
- Could not check: Clio signup flow and language list.

## 3. Polish demand signals
- Autocomplete: "program dla kancelarii" → "… prawnej", "… adwokackich", "legalis program dla kancelarii", "lex program dla kancelarii"; "e-doręczenia kancelaria" → "e doręczenia kancelaria prawna", "… adwokacka"; "program do kancelarii prawnej cena" → none; "portal informacyjny sądów powiadomienia" → none.
- Market size: ~22.9k practising adwokaci and ~42.7k practising radcy prawni (mid-2025, per a Sejm interpellation answer citing the bar bodies) ([Sejm PDF](https://api.sejm.gov.pl/sejm/term10/interpellations/attachment/ATTDMXK2C/i12392-o1.pdf)); most work in small firms (not quantified here).

## 4. What adaptation needs
M52 Polish legal language and forms; Portal Informacyjny Sądów Powszechnych (PISP: mandatory e-doręczenia of court letters to professional attorneys, deadlines run from portal delivery), e-Doręczenia (state e-delivery), e-Sąd/EPU, KRS/CEIDG (M09/M10) and EKW (M27) lookups, KPC deadline rules, tajemnica adwokacka/radcowska (professional secrecy) and RODO for hosting, M46 Fakturownia/inFakt invoicing, M50 VAT invoices.

## 5. Demographic or social driver
DD7 labour scarcity (legal secretaries); none demographic beyond that.

## 6. CEE check
No CZ/SK/RO/HU practice-operations AI in R6; Romanian legal tools are consumer Q&A (TH13) ([R6 catalogue](../../catalogue/R6-cee-peers.csv)).

## 7. Verdict: **partial**
Practice-management software is crowded (30+ programs, Wolters Kluwer bundling) and research is taken (TH07), but the JUPUS-style AI secretariat that handles intake, reads PISP deliveries and computes deadlines is not on the Polish market. Small firms buy slowly and on trust; Wolters Kluwer or Beck can add this inside their suites.

**Seed idea:** "Sekretariat PISP": agent that pulls new deliveries from Portal Informacyjny Sądów and e-Doręczenia each morning, classifies each pismo, computes the KPC/KPK deadline from the delivery date, puts it in the firm's calendar, drafts a client update email and a first-draft response outline; per attorney per month (e.g. 99–149 PLN). Needs PISP access via the attorney's own login (automation terms to verify).
